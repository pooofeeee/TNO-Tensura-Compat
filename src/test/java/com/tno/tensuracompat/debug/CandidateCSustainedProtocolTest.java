package com.tno.tensuracompat.debug;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CandidateCSustainedProtocolTest {
    @Test void ceilingResidueDoesNotCreateAFalseStateB() {
        assertEquals("C", CandidateCSustainedProtocol.state(9984.5126953125, 9984.513179779, 500));
        assertEquals("B", CandidateCSustainedProtocol.state(9784.5, 9984.5, 500));
        assertEquals("A", CandidateCSustainedProtocol.state(9484.5, 9984.5, 500));
    }
    @Test void formulaUsesActualLegalSpaceIndependentlyOfClassification() {
        assertEquals(0.005, CandidateCSustainedProtocol.expected(9990, 9990.005, 500), 1e-9);
        assertEquals(200, CandidateCSustainedProtocol.expected(9790, 9990, 500));
        assertEquals(0, CandidateCSustainedProtocol.expected(9995, 9990, 500));
    }
    @Test void permitsFloatRoundingButRejectsHealingWoundedHpAndShp() {
        assertDoesNotThrow(() -> CandidateCSustainedProtocol.requireTransaction(
                9990, 100, 9.9996, 10000, 500, 9990, 100, 9.9996));
        assertThrows(IllegalStateException.class, () -> CandidateCSustainedProtocol.requireTransaction(
                9990, 100, 10, 10000, 500, 9991, 100, 10));
        assertThrows(IllegalStateException.class, () -> CandidateCSustainedProtocol.requireTransaction(
                9490, 100, 10, 10000, 500, 9990, 101, 10));
    }
    @Test void convergenceDoesNotConfuseStartupBurstWithLateProgress() {
        assertFalse(CandidateCSustainedProtocol.stable(200, 0.2));
        assertTrue(CandidateCSustainedProtocol.stable(0.25, 0.251));
        assertEquals(0.25, CandidateCSustainedProtocol.slope(10000, 9992.5, 600));
        assertTrue(CandidateCSustainedProtocol.stable(0, 0));
    }
}
