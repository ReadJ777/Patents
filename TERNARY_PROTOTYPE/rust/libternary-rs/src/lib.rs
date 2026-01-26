//! ZIME Ternary Computing System
//! Patent Application: 63/967,611
//! 
//! For GOD Alone. Fearing GOD Alone. 🦅

use rand::Rng;

/// Ternary State (Trit)
/// OFF = 0, PSI = Ψ (uncertain), ON = 1
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum TernaryState {
    Off = 0,
    Psi = 1,  // Ψ = 0.5 ± δ
    On = 2,
}

impl TernaryState {
    /// Create from numeric value
    pub fn from_numeric(value: f64, delta: f64) -> Self {
        if value >= 1.0 - delta {
            Self::On
        } else if value <= delta {
            Self::Off
        } else {
            Self::Psi
        }
    }
    
    /// To numeric value
    pub fn to_numeric(self) -> f64 {
        match self {
            Self::Off => 0.0,
            Self::Psi => 0.5,
            Self::On => 1.0,
        }
    }
    
    /// Symbol representation
    pub fn symbol(self) -> &'static str {
        match self {
            Self::Off => "🔴",
            Self::Psi => "🟡",
            Self::On => "🟢",
        }
    }
}

/// Ternary Logic Operations (Kleene 3-valued logic)
pub struct TernaryLogic;

impl TernaryLogic {
    /// AND3: OFF if any OFF, ON if both ON, else PSI
    #[inline]
    pub fn and3(a: TernaryState, b: TernaryState) -> TernaryState {
        match (a, b) {
            (TernaryState::Off, _) | (_, TernaryState::Off) => TernaryState::Off,
            (TernaryState::On, TernaryState::On) => TernaryState::On,
            _ => TernaryState::Psi,
        }
    }
    
    /// OR3: ON if any ON, OFF if both OFF, else PSI
    #[inline]
    pub fn or3(a: TernaryState, b: TernaryState) -> TernaryState {
        match (a, b) {
            (TernaryState::On, _) | (_, TernaryState::On) => TernaryState::On,
            (TernaryState::Off, TernaryState::Off) => TernaryState::Off,
            _ => TernaryState::Psi,
        }
    }
    
    /// NOT3: Inverts ON/OFF, PSI stays PSI
    #[inline]
    pub fn not3(a: TernaryState) -> TernaryState {
        match a {
            TernaryState::On => TernaryState::Off,
            TernaryState::Off => TernaryState::On,
            TernaryState::Psi => TernaryState::Psi,
        }
    }
    
    /// XOR3: PSI if any PSI, else standard XOR
    #[inline]
    pub fn xor3(a: TernaryState, b: TernaryState) -> TernaryState {
        match (a, b) {
            (TernaryState::Psi, _) | (_, TernaryState::Psi) => TernaryState::Psi,
            (x, y) if x == y => TernaryState::Off,
            _ => TernaryState::On,
        }
    }
}

/// PSI State Resolver
pub struct PsiResolver {
    delta: f64,
}

impl PsiResolver {
    pub fn new(delta: f64) -> Self {
        Self { delta }
    }
    
    /// Resolve PSI state probabilistically
    pub fn resolve(&self, psi_value: f64) -> TernaryState {
        let mut rng = rand::thread_rng();
        let resolved = psi_value + rng.gen_range(-self.delta..self.delta);
        
        if resolved >= 0.5 {
            TernaryState::On
        } else {
            TernaryState::Off
        }
    }
}

/// Decision maker using ternary logic
pub struct TernaryDecision {
    delta: f64,
}

impl TernaryDecision {
    pub fn new(delta: f64) -> Self {
        Self { delta }
    }
    
    /// Make ternary decision based on confidence
    #[inline]
    pub fn decide(&self, confidence: f64) -> TernaryState {
        if confidence >= 1.0 - self.delta {
            TernaryState::On
        } else if confidence <= self.delta {
            TernaryState::Off
        } else {
            TernaryState::Psi
        }
    }
}

// C FFI exports
#[no_mangle]
pub extern "C" fn ternary_and3(a: u8, b: u8) -> u8 {
    let a = match a { 0 => TernaryState::Off, 2 => TernaryState::On, _ => TernaryState::Psi };
    let b = match b { 0 => TernaryState::Off, 2 => TernaryState::On, _ => TernaryState::Psi };
    TernaryLogic::and3(a, b) as u8
}

#[no_mangle]
pub extern "C" fn ternary_or3(a: u8, b: u8) -> u8 {
    let a = match a { 0 => TernaryState::Off, 2 => TernaryState::On, _ => TernaryState::Psi };
    let b = match b { 0 => TernaryState::Off, 2 => TernaryState::On, _ => TernaryState::Psi };
    TernaryLogic::or3(a, b) as u8
}

#[no_mangle]
pub extern "C" fn ternary_decide(confidence: f64, delta: f64) -> u8 {
    let td = TernaryDecision::new(delta);
    td.decide(confidence) as u8
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_and3() {
        assert_eq!(TernaryLogic::and3(TernaryState::On, TernaryState::On), TernaryState::On);
        assert_eq!(TernaryLogic::and3(TernaryState::On, TernaryState::Off), TernaryState::Off);
        assert_eq!(TernaryLogic::and3(TernaryState::Psi, TernaryState::On), TernaryState::Psi);
    }
    
    #[test]
    fn test_or3() {
        assert_eq!(TernaryLogic::or3(TernaryState::On, TernaryState::Off), TernaryState::On);
        assert_eq!(TernaryLogic::or3(TernaryState::Off, TernaryState::Off), TernaryState::Off);
        assert_eq!(TernaryLogic::or3(TernaryState::Psi, TernaryState::Off), TernaryState::Psi);
    }
    
    #[test]
    fn test_decision() {
        let td = TernaryDecision::new(0.05);
        assert_eq!(td.decide(0.99), TernaryState::On);
        assert_eq!(td.decide(0.01), TernaryState::Off);
        assert_eq!(td.decide(0.50), TernaryState::Psi);
    }
}
