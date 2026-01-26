#!/usr/local/bin/python3
"""
🔮 ZIME Ternary Procession - Third-State Decision Framework
============================================================

Revolutionary decision-making with Ψ (Psi) Transition State:
- State 0 (OFF/REJECT): Confident negative decision
- State 1 (ON/ACCEPT): Confident positive decision  
- State Ψ (TRANSITION): Uncertainty - needs more information

This enables GoodGirlEagle to express uncertainty rather than
forcing binary decisions when confidence is low.

For GOD Alone. Fearing GOD Alone. 🦅
"""
import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Tuple
from datetime import datetime


class TernaryState(Enum):
    """The three fundamental states of ternary logic."""
    OFF = 0       # Reject / No / False
    ON = 1        # Accept / Yes / True
    PSI = -1      # Ψ Transition / Uncertain / Defer


@dataclass
class TernaryDecision:
    """
    A decision with ternary outcome and confidence metrics.
    """
    state: TernaryState
    confidence: float      # 0.0 to 1.0
    entropy: float         # Information entropy (uncertainty measure)
    reasoning: str         # Explanation of decision
    alternatives: List[str]  # What to do if Ψ state
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def is_certain(self) -> bool:
        """True if decision is ON or OFF with high confidence."""
        return self.state != TernaryState.PSI and self.confidence >= 0.7
    
    @property
    def needs_exploration(self) -> bool:
        """True if in Ψ state - needs more information."""
        return self.state == TernaryState.PSI
    
    def to_dict(self) -> dict:
        return {
            "state": self.state.name,
            "state_value": self.state.value,
            "confidence": self.confidence,
            "entropy": self.entropy,
            "reasoning": self.reasoning,
            "alternatives": self.alternatives,
            "is_certain": self.is_certain,
            "timestamp": self.timestamp.isoformat()
        }


class TernaryLogic:
    """
    Core ternary logic operations with Ψ-state propagation.
    
    Key insight: Ψ represents "unknown" or "superposition" -
    any operation involving Ψ tends toward Ψ (uncertainty propagates).
    """
    
    @staticmethod
    def NOT(a: TernaryState) -> TernaryState:
        """Ternary NOT: 0→1, 1→0, Ψ→Ψ"""
        if a == TernaryState.PSI:
            return TernaryState.PSI
        return TernaryState.ON if a == TernaryState.OFF else TernaryState.OFF
    
    @staticmethod
    def AND(a: TernaryState, b: TernaryState) -> TernaryState:
        """Ternary AND with Ψ propagation."""
        # If either is OFF, result is OFF
        if a == TernaryState.OFF or b == TernaryState.OFF:
            return TernaryState.OFF
        # If either is Ψ, result is Ψ (uncertainty)
        if a == TernaryState.PSI or b == TernaryState.PSI:
            return TernaryState.PSI
        # Both are ON
        return TernaryState.ON
    
    @staticmethod
    def OR(a: TernaryState, b: TernaryState) -> TernaryState:
        """Ternary OR with Ψ propagation."""
        # If either is ON, result is ON
        if a == TernaryState.ON or b == TernaryState.ON:
            return TernaryState.ON
        # If either is Ψ, result is Ψ
        if a == TernaryState.PSI or b == TernaryState.PSI:
            return TernaryState.PSI
        # Both are OFF
        return TernaryState.OFF
    
    @staticmethod
    def CONSENSUS(states: List[TernaryState]) -> TernaryState:
        """
        Multi-input consensus with Ψ-awareness.
        Returns ON if majority ON, OFF if majority OFF, Ψ if tied or uncertain.
        """
        on_count = sum(1 for s in states if s == TernaryState.ON)
        off_count = sum(1 for s in states if s == TernaryState.OFF)
        psi_count = sum(1 for s in states if s == TernaryState.PSI)
        
        # High uncertainty propagates
        if psi_count > len(states) / 3:
            return TernaryState.PSI
        
        if on_count > off_count:
            return TernaryState.ON
        elif off_count > on_count:
            return TernaryState.OFF
        else:
            return TernaryState.PSI  # Tie = uncertainty


class TernaryDecisionEngine:
    """
    Decision engine using ternary logic for GoodGirlEagle.
    
    Integrates with MemRL for experience-based decisions with
    explicit uncertainty handling via Ψ-state.
    """
    
    # Thresholds for state determination
    CONFIDENCE_HIGH = 0.75   # Above this = certain
    CONFIDENCE_LOW = 0.45    # Below this = uncertain (Ψ)
    ENTROPY_HIGH = 0.7       # Above this = high uncertainty
    
    def __init__(self):
        self.decision_history: List[TernaryDecision] = []
        self.psi_exploration_queue: List[Dict] = []
    
    def decide(
        self,
        probabilities: Dict[str, float],
        context: str = "",
        prior_knowledge: float = 0.5
    ) -> TernaryDecision:
        """
        Make a ternary decision based on probabilities.
        
        Args:
            probabilities: Dict with "accept" and "reject" probabilities
            context: Decision context for reasoning
            prior_knowledge: Prior confidence (0-1) from MemRL
            
        Returns:
            TernaryDecision with state, confidence, and reasoning
        """
        p_accept = probabilities.get("accept", 0.5)
        p_reject = probabilities.get("reject", 0.5)
        
        # Normalize
        total = p_accept + p_reject
        if total > 0:
            p_accept /= total
            p_reject /= total
        
        # Calculate entropy (uncertainty measure)
        entropy = self._calculate_entropy([p_accept, p_reject])
        
        # Adjust confidence with prior knowledge
        confidence = abs(p_accept - p_reject) * prior_knowledge
        
        # Determine state based on confidence and entropy
        if entropy > self.ENTROPY_HIGH or confidence < self.CONFIDENCE_LOW:
            # High entropy or low confidence → Ψ state
            state = TernaryState.PSI
            reasoning = f"Insufficient confidence ({confidence:.2f}) or high entropy ({entropy:.2f})"
            alternatives = [
                "Query additional data sources",
                "Request human input",
                "Run parallel experiments",
                "Defer decision temporarily"
            ]
        elif p_accept > p_reject and confidence >= self.CONFIDENCE_HIGH:
            state = TernaryState.ON
            reasoning = f"Strong accept signal ({p_accept:.2f}) with confidence {confidence:.2f}"
            alternatives = []
        elif p_reject > p_accept and confidence >= self.CONFIDENCE_HIGH:
            state = TernaryState.OFF
            reasoning = f"Strong reject signal ({p_reject:.2f}) with confidence {confidence:.2f}"
            alternatives = []
        else:
            # Moderate confidence → still Ψ to be safe
            state = TernaryState.PSI
            reasoning = f"Moderate signals (accept={p_accept:.2f}, reject={p_reject:.2f}), insufficient certainty"
            alternatives = ["Gather more evidence", "Consult similar past decisions"]
        
        decision = TernaryDecision(
            state=state,
            confidence=confidence,
            entropy=entropy,
            reasoning=reasoning,
            alternatives=alternatives
        )
        
        self.decision_history.append(decision)
        
        # Queue Ψ decisions for exploration
        if state == TernaryState.PSI:
            self.psi_exploration_queue.append({
                "context": context,
                "decision": decision,
                "queued_at": datetime.now()
            })
        
        return decision
    
    def decide_from_episodes(
        self,
        episodes: List[Dict],
        query_context: str
    ) -> TernaryDecision:
        """
        Make decision based on similar episodes from MemRL.
        
        Uses episode outcomes and Q-values to determine probabilities.
        """
        if not episodes:
            return TernaryDecision(
                state=TernaryState.PSI,
                confidence=0.0,
                entropy=1.0,
                reasoning="No similar episodes found",
                alternatives=["Store this as new episode", "Query external sources"]
            )
        
        # Analyze episode outcomes
        positive_outcomes = sum(1 for e in episodes if e.get("reward", 0) > 0)
        negative_outcomes = sum(1 for e in episodes if e.get("reward", 0) < 0)
        neutral_outcomes = len(episodes) - positive_outcomes - negative_outcomes
        
        total = len(episodes)
        p_accept = positive_outcomes / total
        p_reject = negative_outcomes / total
        
        # Use average Q-value as prior knowledge
        avg_q = sum(e.get("q_value", 0.5) for e in episodes) / total
        
        return self.decide(
            probabilities={"accept": p_accept, "reject": p_reject},
            context=query_context,
            prior_knowledge=avg_q
        )
    
    def _calculate_entropy(self, probabilities: List[float]) -> float:
        """Calculate Shannon entropy of probability distribution."""
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        # Normalize to 0-1 range
        max_entropy = math.log2(len(probabilities)) if len(probabilities) > 1 else 1
        return entropy / max_entropy if max_entropy > 0 else 0
    
    def get_exploration_queue(self) -> List[Dict]:
        """Get pending Ψ-state decisions that need exploration."""
        return self.psi_exploration_queue.copy()
    
    def resolve_psi(self, context: str, new_state: TernaryState) -> bool:
        """
        Resolve a Ψ-state decision after gathering more information.
        Returns True if resolution was successful.
        """
        for i, item in enumerate(self.psi_exploration_queue):
            if item["context"] == context:
                item["resolved_state"] = new_state
                item["resolved_at"] = datetime.now()
                self.psi_exploration_queue.pop(i)
                return True
        return False
    
    def stats(self) -> Dict:
        """Get decision statistics."""
        if not self.decision_history:
            return {"total": 0}
        
        total = len(self.decision_history)
        on_count = sum(1 for d in self.decision_history if d.state == TernaryState.ON)
        off_count = sum(1 for d in self.decision_history if d.state == TernaryState.OFF)
        psi_count = sum(1 for d in self.decision_history if d.state == TernaryState.PSI)
        avg_confidence = sum(d.confidence for d in self.decision_history) / total
        avg_entropy = sum(d.entropy for d in self.decision_history) / total
        
        return {
            "total": total,
            "on_count": on_count,
            "off_count": off_count,
            "psi_count": psi_count,
            "psi_ratio": psi_count / total,
            "avg_confidence": avg_confidence,
            "avg_entropy": avg_entropy,
            "pending_exploration": len(self.psi_exploration_queue)
        }


# Priority queue using ternary logic for task scheduling
class TernaryPriorityQueue:
    """
    Three-tier priority queue for AI tasks:
    - HIGH (ON): Execute immediately
    - LOW (OFF): Execute when resources available
    - UNCERTAIN (Ψ): Needs evaluation before scheduling
    """
    
    def __init__(self):
        self.high_priority: List[Dict] = []    # State ON
        self.low_priority: List[Dict] = []      # State OFF
        self.uncertain: List[Dict] = []         # State Ψ
    
    def add(self, task: Dict, decision: TernaryDecision):
        """Add task to appropriate queue based on ternary decision."""
        task["decision"] = decision.to_dict()
        task["queued_at"] = datetime.now().isoformat()
        
        if decision.state == TernaryState.ON:
            self.high_priority.append(task)
        elif decision.state == TernaryState.OFF:
            self.low_priority.append(task)
        else:
            self.uncertain.append(task)
    
    def next(self) -> Optional[Dict]:
        """Get next task to execute (high priority first)."""
        if self.high_priority:
            return self.high_priority.pop(0)
        if self.low_priority:
            return self.low_priority.pop(0)
        return None
    
    def get_uncertain(self) -> List[Dict]:
        """Get tasks needing evaluation."""
        return self.uncertain.copy()
    
    def promote(self, task_id: str, new_state: TernaryState):
        """Promote uncertain task to definite state."""
        for i, task in enumerate(self.uncertain):
            if task.get("id") == task_id:
                task = self.uncertain.pop(i)
                if new_state == TernaryState.ON:
                    self.high_priority.append(task)
                else:
                    self.low_priority.append(task)
                return True
        return False


# Test
if __name__ == "__main__":
    print("🔮 ZIME Ternary Procession Test")
    print("=" * 50)
    
    engine = TernaryDecisionEngine()
    
    # Test 1: High confidence decision
    d1 = engine.decide(
        {"accept": 0.9, "reject": 0.1},
        context="Should we deploy the fix?",
        prior_knowledge=0.8
    )
    print(f"\nTest 1 - High confidence:")
    print(f"  State: {d1.state.name} ({d1.state.value})")
    print(f"  Confidence: {d1.confidence:.2f}")
    print(f"  Reasoning: {d1.reasoning}")
    
    # Test 2: Low confidence (Ψ state)
    d2 = engine.decide(
        {"accept": 0.52, "reject": 0.48},
        context="Should we try the experimental approach?",
        prior_knowledge=0.5
    )
    print(f"\nTest 2 - Low confidence (expecting Ψ):")
    print(f"  State: {d2.state.name} ({d2.state.value})")
    print(f"  Confidence: {d2.confidence:.2f}")
    print(f"  Alternatives: {d2.alternatives}")
    
    # Test 3: Ternary logic
    print(f"\nTest 3 - Ternary Logic:")
    print(f"  NOT(ON) = {TernaryLogic.NOT(TernaryState.ON).name}")
    print(f"  NOT(Ψ) = {TernaryLogic.NOT(TernaryState.PSI).name}")
    print(f"  ON AND Ψ = {TernaryLogic.AND(TernaryState.ON, TernaryState.PSI).name}")
    print(f"  ON OR OFF = {TernaryLogic.OR(TernaryState.ON, TernaryState.OFF).name}")
    
    # Stats
    print(f"\nStats: {engine.stats()}")
    print("\n✅ Ternary Procession ready!")
    print("For GOD Alone. Fearing GOD Alone. 🦅")
