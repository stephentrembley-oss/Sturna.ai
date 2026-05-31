"""Auction API — Coalition Market Auction operations."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.auction import Auction, AuctionBid, AuctionStatus, BidStatus
from app.models.agent import Agent

router = APIRouter()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_auction(
    intent_id: str,
    intent_text: str,
    intent_category: str,
    coalition: str,
    db: AsyncSession = Depends(get_db),
):
    """Create a new Coalition Market Auction for an intent."""
    auction = Auction(
        intent_id=intent_id,
        intent_text=intent_text,
        intent_category=intent_category,
        coalition=coalition,
        status=AuctionStatus.PENDING.value,
    )
    db.add(auction)
    await db.commit()
    await db.refresh(auction)

    return {
        "auction_id": str(auction.id),
        "intent_id": intent_id,
        "coalition": coalition,
        "status": auction.status,
        "created_at": auction.created_at.isoformat(),
    }


@router.get("/{auction_id}")
async def get_auction(auction_id: str, db: AsyncSession = Depends(get_db)):
    """Get auction status and results."""
    result = await db.execute(select(Auction).where(Auction.id == auction_id))
    auction = result.scalar_one_or_none()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    return auction.to_dict()


@router.post("/{auction_id}/bid")
async def submit_bid(
    auction_id: str,
    agent_id: str,
    confidence_score: float,
    estimated_cost: float = 0.0,
    estimated_latency_ms: float = 0.0,
    capability_match_score: float = 0.0,
    encrypted_payload: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Submit a sealed bid from an agent."""
    auction_result = await db.execute(
        select(Auction).where(Auction.id == auction_id)
    )
    auction = auction_result.scalar_one_or_none()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    if auction.status != AuctionStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Auction is not open for bidding")

    bid = AuctionBid(
        auction_id=auction_id,
        agent_id=agent_id,
        confidence_score=confidence_score,
        estimated_cost=estimated_cost,
        estimated_latency_ms=estimated_latency_ms,
        capability_match_score=capability_match_score,
        encrypted_payload=encrypted_payload,
    )

    db.add(bid)
    await db.commit()
    await db.refresh(bid)

    return {
        "bid_id": str(bid.id),
        "auction_id": auction_id,
        "agent_id": agent_id,
        "status": bid.status,
    }


@router.get("/{auction_id}/bids")
async def list_bids(auction_id: str, db: AsyncSession = Depends(get_db)):
    """List all bids for an auction (visible after close)."""
    result = await db.execute(
        select(AuctionBid).where(AuctionBid.auction_id == auction_id)
    )
    bids = result.scalars().all()
    return {
        "auction_id": auction_id,
        "bid_count": len(bids),
        "bids": [b.to_dict() for b in bids],
    }


@router.post("/{auction_id}/execute")
async def execute_auction(auction_id: str, db: AsyncSession = Depends(get_db)):
    """Close bidding, select winner via VCG, execute intent."""
    auction_result = await db.execute(select(Auction).where(Auction.id == auction_id))
    auction = auction_result.scalar_one_or_none()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    bids_result = await db.execute(
        select(AuctionBid)
        .where(AuctionBid.auction_id == auction_id)
        .where(AuctionBid.status == BidStatus.SUBMITTED.value)
    )
    bids = bids_result.scalars().all()

    if not bids:
        raise HTTPException(status_code=400, detail="No bids submitted")

    winner = max(bids, key=lambda b: b.confidence_score)

    await db.execute(
        update(AuctionBid)
        .where(AuctionBid.id == winner.id)
        .values(status=BidStatus.WON.value)
    )

    for bid in bids:
        if bid.id != winner.id:
            await db.execute(
                update(AuctionBid)
                .where(AuctionBid.id == bid.id)
                .values(status=BidStatus.LOST.value)
            )

    await db.execute(
        update(Auction)
        .where(Auction.id == auction_id)
        .values(
            status=AuctionStatus.COMPLETED.value,
            winner_agent_id=winner.agent_id,
            winner_bid_id=str(winner.id),
            winner_confidence=winner.confidence_score,
            vcg_price=winner.estimated_cost,
            completed_at=func.now(),
        )
    )

    await db.commit()

    return {
        "auction_id": auction_id,
        "status": "completed",
        "winner_agent_id": winner.agent_id,
        "winner_confidence": winner.confidence_score,
        "vcg_price": winner.estimated_cost,
    }


@router.get("/{auction_id}/proof")
async def get_proof(auction_id: str, db: AsyncSession = Depends(get_db)):
    """Get zk-SNARK proof for auction execution."""
    result = await db.execute(select(Auction).where(Auction.id == auction_id))
    auction = result.scalar_one_or_none()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    return {
        "auction_id": auction_id,
        "proof_id": auction.proof_id,
        "proof_status": auction.proof_status,
        "proof_data": auction.proof_data,
    }


@router.get("/live")
async def live_auctions(db: AsyncSession = Depends(get_db)):
    """Get currently active auctions for live dashboard."""
    result = await db.execute(
        select(Auction)
        .where(Auction.status.in_([AuctionStatus.PENDING.value, AuctionStatus.ACTIVE.value]))
        .order_by(Auction.created_at.desc())
        .limit(20)
    )
    auctions = result.scalars().all()
    return {
        "active_count": len(auctions),
        "auctions": [a.to_dict() for a in auctions],
    }