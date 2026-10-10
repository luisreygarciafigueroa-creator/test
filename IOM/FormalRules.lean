import IOM.Specification

namespace IOM

/-!
# Reglas formales del marco I.O. (espejo, creates, vectores)

Predicados Lean que codifican las reglas estructurales de la especificación
operativa. Las relaciones generadas desde JSON deben satisfacerlos;
la comprobación automática está en `tests/test_formal_rules_bridge.py`.
-/

/-- Nodo estructural mínimo: fase + posición (sin etiqueta léxica). -/
structure TriadNode where
  phase : TriadPhase
  pos   : TriadPosition
  deriving DecidableEq, Repr

/-- Fase opuesta. -/
def TriadPhase.opposite : TriadPhase → TriadPhase
  | .advance => .retreat
  | .retreat => .advance

theorem opposite_involutive (p : TriadPhase) : p.opposite.opposite = p := by
  cases p <;> rfl

theorem opposite_ne (p : TriadPhase) : p.opposite ≠ p := by
  cases p <;> decide

/-- `mirrorOf`: fase opuesta y posición espejada. -/
def isMirror (a b : TriadNode) : Prop :=
  a.phase.opposite = b.phase ∧ a.pos.mirror = b.pos

theorem isMirror_implies_opposite_phase (a b : TriadNode) (h : isMirror a b) :
    a.phase ≠ b.phase := by
  intro heq
  have : a.phase.opposite = a.phase := by
    calc a.phase.opposite = b.phase := h.1
      _ = a.phase := heq.symm
  exact opposite_ne a.phase this

theorem isMirror_implies_mirrored_pos (a b : TriadNode) (h : isMirror a b) :
    b.pos = a.pos.mirror := h.2.symm

/-- Las cuatro reglas de creación entre fases opuestas. -/
def lateral (p : TriadPosition) : Prop := p = .left ∨ p = .right

def isCreates (a b : TriadNode) : Prop :=
  a.phase.opposite = b.phase ∧
    ((lateral a.pos ∧ b.pos = .center) ∨ (a.pos = .center ∧ lateral b.pos))

/-- Conteos canónicos derivados de las reglas (13 tríadas). -/
def expectedMirrorDirected : Nat := 78
def expectedCreatesDirected : Nat := 104
def expectedNoneDirected : Nat := 208
def expectedVectorSteps : Nat := 20
def expectedNodes : Nat := 78

theorem expected_partition :
    expectedMirrorDirected + expectedCreatesDirected + expectedNoneDirected = 390 := by
  native_decide

theorem expected_nodes_formula : expectedNodes = 13 * 2 * 3 := by native_decide

theorem expected_vector_steps_formula : expectedVectorSteps = 4 * 5 := by native_decide

/-- Índice de eje en $[0,4]$. -/
theorem axis_bound (n : Nat) (h : n ≤ 4) : n ≤ 4 := h

/-- Simetría del eje en secuencias de retroceso. -/
theorem axis_retreat_involution (n : Nat) (h : n ≤ 4) : 4 - (4 - n) = n := by omega

end IOM
