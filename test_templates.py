#!/usr/bin/env python3
"""Test that templates are correctly configured with Jinja2."""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

def test_templates():
    """Test that all templates can be loaded and rendered."""
    
    templates_dir = Path("templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    # List of templates to test
    templates_to_test = [
        "index.html",
        "groups.html",
        "students.html",
        "attendance.html",
        "payments_new.html",
        "payments.html",
        "settings.html",
        "statistics.html",
        "tournaments.html",
        "login.html",
        "offline.html",
    ]
    
    print("🔍 Testing Jinja2 template rendering...\n")
    
    errors = []
    success_count = 0
    
    for template_name in templates_to_test:
        try:
            template = env.get_template(template_name)
            # Try to render with minimal context
            html = template.render(request={"url": "/", "method": "GET"})
            
            # Check that the rendered HTML contains expected elements
            checks = {
                "favicon": '/static/icons/sa_logo.png' in html,
                "app_icon_144": '/static/icons/sa_logo_blue-144.png' in html,
                "app_icon_512": '/static/icons/sa_logo_blue-512.png' in html,
                "has_doctype": '<!DOCTYPE html>' in html,
                "has_html_tag": '<html' in html,
            }
            
            all_checks_passed = all(checks.values())
            
            if all_checks_passed:
                print(f"✅ {template_name}: OK")
                success_count += 1
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                print(f"⚠️  {template_name}: Missing - {', '.join(failed_checks)}")
                errors.append(f"{template_name}: {failed_checks}")
                
        except TemplateNotFound:
            print(f"❌ {template_name}: Template not found")
            errors.append(f"{template_name}: Not found")
        except Exception as e:
            print(f"❌ {template_name}: Error - {str(e)}")
            errors.append(f"{template_name}: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"✅ Passed: {success_count}/{len(templates_to_test)}")
    
    if errors:
        print(f"❌ Failed: {len(errors)}")
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("🎉 All templates rendered successfully!")
        print("\n✨ Favicon and app icons are correctly inherited from base templates")
        return True

if __name__ == "__main__":
    import sys
    success = test_templates()
    sys.exit(0 if success else 1)
