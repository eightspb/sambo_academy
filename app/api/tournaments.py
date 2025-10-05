"""Tournaments API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import uuid

from app.database import get_db
from app.models.user import User
from app.models.tournament import Tournament, TournamentParticipation
from app.models.student import Student
from app.schemas.tournament import (
    TournamentCreate,
    TournamentUpdate,
    TournamentResponse,
    ParticipationCreate,
    ParticipationUpdate,
    ParticipationResponse,
    ParticipationWithDetails,
    StudentTournamentStats
)
from app.core.security import get_current_user
from app.core.permissions import check_student_access

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


@router.get("", response_model=List[TournamentResponse])
async def get_tournaments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tournaments."""
    result = await db.execute(
        select(Tournament).order_by(Tournament.tournament_date.desc())
    )
    tournaments = result.scalars().all()
    
    return tournaments


@router.post("", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
async def create_tournament(
    tournament_data: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tournament."""
    new_tournament = Tournament(
        **tournament_data.model_dump(),
        created_by=current_user.id
    )
    
    db.add(new_tournament)
    await db.commit()
    await db.refresh(new_tournament)
    
    return new_tournament


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific tournament."""
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    return tournament


@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: uuid.UUID,
    tournament_data: TournamentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a tournament."""
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Update fields
    update_data = tournament_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tournament, field, value)
    
    await db.commit()
    await db.refresh(tournament)
    
    return tournament


@router.delete("/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(
    tournament_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a tournament and all its participants."""
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Delete tournament (participants will be deleted automatically due to cascade)
    await db.delete(tournament)
    await db.commit()
    
    return None


@router.post("/{tournament_id}/participants", response_model=ParticipationResponse, status_code=status.HTTP_201_CREATED)
async def add_tournament_participant(
    tournament_id: uuid.UUID,
    participation_data: ParticipationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a participant to a tournament."""
    # Verify tournament exists
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Verify student access
    await check_student_access(participation_data.student_id, current_user, db)
    
    # Check if student is already a participant
    existing = await db.execute(
        select(TournamentParticipation).where(
            TournamentParticipation.tournament_id == tournament_id,
            TournamentParticipation.student_id == participation_data.student_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот ученик уже добавлен в турнир"
        )
    
    # Create participation
    new_participation = TournamentParticipation(
        tournament_id=tournament_id,
        **participation_data.model_dump()
    )
    
    db.add(new_participation)
    await db.commit()
    await db.refresh(new_participation)
    
    return new_participation


@router.get("/{tournament_id}/results", response_model=List[ParticipationWithDetails])
async def get_tournament_results(
    tournament_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all results for a tournament."""
    result = await db.execute(
        select(TournamentParticipation, Student.full_name, Tournament.name, Tournament.tournament_date)
        .join(Student, TournamentParticipation.student_id == Student.id)
        .join(Tournament, TournamentParticipation.tournament_id == Tournament.id)
        .where(TournamentParticipation.tournament_id == tournament_id)
        .order_by(TournamentParticipation.place)
    )
    
    participations = result.all()
    
    return [
        ParticipationWithDetails(
            **participation.__dict__,
            student_name=student_name,
            tournament_name=tournament_name,
            tournament_date=tournament_date
        )
        for participation, student_name, tournament_name, tournament_date in participations
    ]


@router.put("/{tournament_id}/participants/{participation_id}", response_model=ParticipationResponse)
async def update_tournament_participant(
    tournament_id: uuid.UUID,
    participation_id: uuid.UUID,
    participation_data: ParticipationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a tournament participant."""
    result = await db.execute(
        select(TournamentParticipation).where(
            TournamentParticipation.id == participation_id,
            TournamentParticipation.tournament_id == tournament_id
        )
    )
    participation = result.scalar_one_or_none()
    
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation not found"
        )
    
    # Verify student access
    await check_student_access(participation.student_id, current_user, db)
    
    # Update fields
    update_data = participation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(participation, field, value)
    
    await db.commit()
    await db.refresh(participation)
    
    return participation


@router.delete("/{tournament_id}/participants/{participation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament_participant(
    tournament_id: uuid.UUID,
    participation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a tournament participant."""
    result = await db.execute(
        select(TournamentParticipation).where(
            TournamentParticipation.id == participation_id,
            TournamentParticipation.tournament_id == tournament_id
        )
    )
    participation = result.scalar_one_or_none()
    
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation not found"
        )
    
    # Verify student access
    await check_student_access(participation.student_id, current_user, db)
    
    await db.delete(participation)
    await db.commit()
    
    return None


@router.get("/students/{student_id}/stats", response_model=StudentTournamentStats)
async def get_student_tournament_statistics(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tournament statistics for a student."""
    # Verify student access
    student = await check_student_access(student_id, current_user, db)
    
    # Get aggregated stats
    stats_result = await db.execute(
        select(
            func.count(TournamentParticipation.id),
            func.sum(TournamentParticipation.total_fights),
            func.sum(TournamentParticipation.wins),
            func.sum(TournamentParticipation.losses),
            func.min(TournamentParticipation.place)
        )
        .where(TournamentParticipation.student_id == student_id)
    )
    
    stats = stats_result.first()
    total_tournaments = stats[0] or 0
    total_fights = stats[1] or 0
    total_wins = stats[2] or 0
    total_losses = stats[3] or 0
    best_place = stats[4]
    
    win_rate = (total_wins / total_fights * 100) if total_fights > 0 else 0.0
    
    # Get all participations with details
    participations_result = await db.execute(
        select(TournamentParticipation, Student.full_name, Tournament.name, Tournament.tournament_date)
        .join(Student, TournamentParticipation.student_id == Student.id)
        .join(Tournament, TournamentParticipation.tournament_id == Tournament.id)
        .where(TournamentParticipation.student_id == student_id)
        .order_by(Tournament.tournament_date.desc())
    )
    
    participations = participations_result.all()
    
    return StudentTournamentStats(
        student_id=student_id,
        student_name=student.full_name,
        total_tournaments=total_tournaments,
        total_fights=total_fights,
        total_wins=total_wins,
        total_losses=total_losses,
        win_rate=round(win_rate, 2),
        best_place=best_place,
        participations=[
            ParticipationWithDetails(
                **participation.__dict__,
                student_name=student_name,
                tournament_name=tournament_name,
                tournament_date=tournament_date
            )
            for participation, student_name, tournament_name, tournament_date in participations
        ]
    )
