"""
Fraud Detection Engine
Multi-signal analysis combining linguistic, acoustic, and behavioral patterns
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from loguru import logger
import math


@dataclass
class FraudSignal:
    """Individual fraud detection signal"""
    signal_type: str  # keyword, pattern, acoustic, behavioral
    category: str  # spam, fraud, phishing, robocall
    description: str
    confidence: float
    weight: float
    evidence: List[str]


class FraudDetector:
    """
    Multi-signal fraud detection engine
    Combines linguistic, acoustic, and behavioral analysis
    """
    
    def __init__(self):
        self._load_detection_rules()
    
    def _load_detection_rules(self):
        """Load fraud detection rules and patterns"""
        
        # Fraud keywords by category with weights
        self.fraud_keywords = {
            "fraud": {
                "high": [
                    "bank account suspended", "verify your account", "unauthorized transaction",
                    "security breach", "account compromised", "wire transfer immediately",
                    "send money", "gift cards", "bitcoin payment", "western union",
                    "money gram", "confirm your identity", "account locked", "IRS",
                    "arrest warrant", "legal action", "court order"
                ],
                "medium": [
                    "verify", "confirm", "urgent action", "immediate response",
                    "update your information", "security alert", "suspicious activity",
                    "temporary hold", "verification required"
                ]
            },
            "phishing": {
                "high": [
                    "social security number", "credit card number", "CVV", "OTP",
                    "one time password", "login credentials", "password reset",
                    "click the link", "verify your password", "personal information",
                    "bank details", "routing number", "account number"
                ],
                "medium": [
                    "verify", "update details", "confirm information", "security code",
                    "pin number", "mother's maiden name", "date of birth"
                ]
            },
            "spam": {
                "high": [
                    "congratulations you won", "lottery winner", "prize winner",
                    "claim your reward", "free offer", "exclusive deal",
                    "you have been selected", "million dollars", "inheritance"
                ],
                "medium": [
                    "limited time", "act now", "special offer", "discount",
                    "promotion", "free trial", "no obligation", "call back"
                ]
            },
            "robocall": {
                "high": [
                    "press 1 to", "press 2 to", "this is an automated message",
                    "pre-recorded", "automated call", "please hold for"
                ],
                "medium": [
                    "your call is important", "do not hang up", "stay on the line",
                    "recording", "representative", "operator"
                ]
            }
        }
        
        # Hindi/Indian language keywords
        self.hindi_keywords = {
            "fraud": [
                "aapka khata", "bank se bol raha", "OTP batao", "paise transfer",
                "lottery jeeta", "KYC update", "aadhar link", "pan card verify",
                "turant bhejo", "account band ho jayega", "verify karo",
                "RBI se", "income tax", "police", "CBI"
            ]
        }
        
        # UPI and Indian payment fraud patterns
        self.upi_fraud_keywords = {
            "high": [
                "UPI payment", "UPI request", "payment is pending", "accept the request",
                "receive money", "collect request", "payment request", "GPay", "PhonePe",
                "Paytm", "BHIM", "₹", "Rs.", "rupees", "lakh", "crore",
                "cashback", "refund pending", "refund request", "KYC expired",
                "KYC update", "link Aadhaar", "link PAN", "bank account blocked",
                "RBI notification", "government scheme", "PM scheme", "subsidy",
                "before it expires", "expires today", "expires soon", "do it now",
                "account will be blocked", "account blocked", "update your Aadhaar",
                "update your PAN", "Aadhaar", "PAN card", "KYC has expired",
                "verify Aadhaar", "verify PAN", "link your", "blocked", "suspended"
            ],
            "medium": [
                "accept request", "pending request", "money transfer", "send money",
                "payment link", "scan QR", "QR code", "collect money", "update immediately",
                "immediately", "urgent", "dear customer"
            ]
        }
        
        # Urgency indicators
        self.urgency_patterns = [
            r"immediately", r"urgent(?:ly)?", r"right now", r"within \d+ hours?",
            r"last chance", r"final warning", r"time sensitive", r"don't delay",
            r"expires? today", r"act fast", r"hurry", r"emergency",
            r"limited time", r"only \d+ (?:hours?|minutes?|days?) left"
        ]
        
        # Threat patterns
        self.threat_patterns = [
            r"arrest", r"warrant", r"legal action", r"sue", r"lawsuit",
            r"police", r"jail", r"prison", r"court", r"penalty",
            r"fine(?:d)?", r"prosecut", r"criminal", r"federal"
        ]
        
        # Request patterns (asking for sensitive info)
        self.request_patterns = [
            r"(?:tell|give|send|share|provide) (?:me |us )?(?:your )?(?:the )?(?:OTP|password|pin|cvv|ssn|account)",
            r"what is your (?:account|password|pin|ssn|social security)",
            r"(?:verify|confirm) your (?:identity|account|details|information)",
            r"need your (?:personal|account|bank|card) (?:information|details|number)"
        ]
        
        # Robocall voice patterns
        self.robocall_patterns = [
            r"press (?:1|2|3|4|5|6|7|8|9|0|one|two|three|four|five)",
            r"para español",
            r"this (?:is|call is) (?:an? )?(?:automated|recorded|pre-recorded)",
            r"you (?:are|have been) (?:selected|chosen|approved)"
        ]
    
    def detect(self, text: str, acoustic_features: Optional[Dict[str, Any]] = None, 
               behavioral_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive fraud detection analysis
        
        Args:
            text: Transcript text to analyze
            acoustic_features: Optional voice/audio characteristics
            behavioral_data: Optional behavioral patterns
        
        Returns:
            Complete analysis results with scores and explanations
        """
        signals: List[FraudSignal] = []
        
        # 1. Linguistic Analysis
        linguistic_signals = self._analyze_linguistic(text)
        signals.extend(linguistic_signals)
        
        # 2. Acoustic Analysis
        if acoustic_features:
            acoustic_signals = self._analyze_acoustic(acoustic_features)
            signals.extend(acoustic_signals)
        
        # 3. Behavioral Analysis
        if behavioral_data:
            behavioral_signals = self._analyze_behavioral(behavioral_data)
            signals.extend(behavioral_signals)
        
        # 4. Pattern Matching
        pattern_signals = self._analyze_patterns(text)
        signals.extend(pattern_signals)
        
        # 5. Calculate composite scores
        scores = self._calculate_scores(signals)
        
        # 6. Determine classification
        classification = self._determine_classification(scores)
        
        # 7. Generate explanation
        explanation = self._generate_explanation(signals, scores, classification)
        
        # 8. Extract highlighted phrases
        highlighted = self._extract_highlights(text, signals)
        
        return {
            "classification": classification,
            "risk_score": scores["overall"],
            "spam_score": scores["spam"],
            "fraud_score": scores["fraud"],
            "phishing_score": scores["phishing"],
            "robocall_score": scores["robocall"],
            "signals": [
                {
                    "type": s.signal_type,
                    "category": s.category,
                    "description": s.description,
                    "confidence": s.confidence,
                    "evidence": s.evidence
                }
                for s in signals
            ],
            "suspicious_keywords": self._extract_keywords(signals),
            "fraud_indicators": self._extract_indicators(signals),
            "highlighted_phrases": highlighted,
            "explanation": explanation,
            "confidence": self._calculate_confidence(signals, scores)
        }
    
    def _analyze_linguistic(self, text: str) -> List[FraudSignal]:
        """Analyze text for linguistic fraud indicators"""
        signals = []
        text_lower = text.lower()
        
        for category, severity_keywords in self.fraud_keywords.items():
            for severity, keywords in severity_keywords.items():
                weight = 1.5 if severity == "high" else 1.0
                
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        signals.append(FraudSignal(
                            signal_type="keyword",
                            category=category,
                            description=f"Detected {severity}-risk {category} keyword: '{keyword}'",
                            confidence=0.9 if severity == "high" else 0.7,
                            weight=weight,
                            evidence=[keyword]
                        ))
        
        # Check Hindi keywords
        for category, keywords in self.hindi_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    signals.append(FraudSignal(
                        signal_type="keyword",
                        category=category,
                        description=f"Detected Hindi {category} keyword: '{keyword}'",
                        confidence=0.85,
                        weight=1.4,
                        evidence=[keyword]
                    ))
        
        # Check UPI/Indian payment fraud keywords
        for severity, keywords in self.upi_fraud_keywords.items():
            weight = 1.5 if severity == "high" else 1.0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    signals.append(FraudSignal(
                        signal_type="keyword",
                        category="fraud",
                        description=f"Detected {severity}-risk UPI/payment fraud keyword: '{keyword}'",
                        confidence=0.9 if severity == "high" else 0.7,
                        weight=weight,
                        evidence=[keyword]
                    ))
        
        return signals
    
    def _analyze_patterns(self, text: str) -> List[FraudSignal]:
        """Analyze text for fraud patterns"""
        signals = []
        text_lower = text.lower()
        
        # Urgency patterns
        urgency_matches = []
        for pattern in self.urgency_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            urgency_matches.extend(matches)
        
        if urgency_matches:
            signals.append(FraudSignal(
                signal_type="pattern",
                category="general",
                description="High urgency language detected",
                confidence=min(0.5 + len(urgency_matches) * 0.1, 0.95),
                weight=1.3,
                evidence=urgency_matches[:5]
            ))
        
        # Threat patterns
        threat_matches = []
        for pattern in self.threat_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            threat_matches.extend(matches)
        
        if threat_matches:
            signals.append(FraudSignal(
                signal_type="pattern",
                category="fraud",
                description="Threatening language detected",
                confidence=min(0.6 + len(threat_matches) * 0.1, 0.95),
                weight=1.5,
                evidence=threat_matches[:5]
            ))
        
        # Request for sensitive info
        request_matches = []
        for pattern in self.request_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            request_matches.extend(matches)
        
        if request_matches:
            signals.append(FraudSignal(
                signal_type="pattern",
                category="phishing",
                description="Request for sensitive information detected",
                confidence=0.9,
                weight=1.6,
                evidence=request_matches[:3]
            ))
        
        # Robocall patterns
        robocall_matches = []
        for pattern in self.robocall_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            robocall_matches.extend(matches)
        
        if robocall_matches:
            signals.append(FraudSignal(
                signal_type="pattern",
                category="robocall",
                description="Automated call patterns detected",
                confidence=0.85,
                weight=1.4,
                evidence=robocall_matches[:3]
            ))
        
        return signals
    
    def _analyze_acoustic(self, features: Dict) -> List[FraudSignal]:
        """Analyze acoustic/voice features"""
        signals = []
        
        # Speaking rate analysis
        speaking_rate = features.get("speaking_rate", 150)  # words per minute
        if speaking_rate > 200:
            signals.append(FraudSignal(
                signal_type="acoustic",
                category="general",
                description="Unusually fast speaking rate detected",
                confidence=0.7,
                weight=1.1,
                evidence=[f"Speaking rate: {speaking_rate} WPM"]
            ))
        
        # Voice stress
        stress_level = features.get("stress_level", 0)
        if stress_level > 0.7:
            signals.append(FraudSignal(
                signal_type="acoustic",
                category="general",
                description="High voice stress detected",
                confidence=stress_level,
                weight=1.2,
                evidence=[f"Stress level: {stress_level:.2f}"]
            ))
        
        # Synthetic voice detection
        synthetic_score = features.get("synthetic_probability", 0)
        if synthetic_score > 0.6:
            signals.append(FraudSignal(
                signal_type="acoustic",
                category="robocall",
                description="Possible synthetic/robotic voice detected",
                confidence=synthetic_score,
                weight=1.5,
                evidence=[f"Synthetic probability: {synthetic_score:.2f}"]
            ))
        
        # Background noise
        if features.get("background_noise_type") == "call_center":
            signals.append(FraudSignal(
                signal_type="acoustic",
                category="spam",
                description="Call center background noise detected",
                confidence=0.6,
                weight=1.0,
                evidence=["Call center ambient noise"]
            ))
        
        return signals
    
    def _analyze_behavioral(self, data: Dict) -> List[FraudSignal]:
        """Analyze behavioral patterns"""
        signals = []
        
        # Caller behavior
        if data.get("interruptions_count", 0) > 5:
            signals.append(FraudSignal(
                signal_type="behavioral",
                category="general",
                description="Aggressive caller behavior - frequent interruptions",
                confidence=0.65,
                weight=1.1,
                evidence=["High interruption count"]
            ))
        
        # Pressure tactics
        if data.get("pressure_score", 0) > 0.7:
            signals.append(FraudSignal(
                signal_type="behavioral",
                category="fraud",
                description="High-pressure tactics detected",
                confidence=data.get("pressure_score", 0.7),
                weight=1.4,
                evidence=["Pressure tactics identified"]
            ))
        
        # Evasiveness
        if data.get("evasiveness_score", 0) > 0.6:
            signals.append(FraudSignal(
                signal_type="behavioral",
                category="fraud",
                description="Evasive responses detected",
                confidence=0.7,
                weight=1.2,
                evidence=["Caller avoids direct questions"]
            ))
        
        return signals
    
    def _calculate_scores(self, signals: List[FraudSignal]) -> Dict[str, float]:
        """Calculate composite scores from all signals"""
        category_scores: Dict[str, float] = {
            "spam": 0.0,
            "fraud": 0.0,
            "phishing": 0.0,
            "robocall": 0.0,
            "general": 0.0
        }
        
        category_weights: Dict[str, float] = {
            "spam": 0.0,
            "fraud": 0.0,
            "phishing": 0.0,
            "robocall": 0.0,
            "general": 0.0
        }
        
        for signal in signals:
            cat = signal.category
            if cat in category_scores:
                category_scores[cat] += signal.confidence * signal.weight
                category_weights[cat] += signal.weight
        
        # Normalize scores
        for cat in category_scores:
            if category_weights[cat] > 0:
                category_scores[cat] = min(category_scores[cat] / max(category_weights[cat], 1), 1.0)
        
        # Calculate overall risk score (0-100)
        max_category_score = max(
            category_scores["spam"],
            category_scores["fraud"],
            category_scores["phishing"],
            category_scores["robocall"]
        )
        
        # Boost overall score if multiple categories are triggered
        active_categories = sum(1 for v in category_scores.values() if v > 0.3)
        category_boost = 1 + (active_categories - 1) * 0.1 if active_categories > 1 else 1
        
        # Include general score as a modifier
        general_modifier = 1 + category_scores["general"] * 0.2
        
        overall = min(max_category_score * category_boost * general_modifier * 100, 100)
        
        return {
            "spam": category_scores["spam"],
            "fraud": category_scores["fraud"],
            "phishing": category_scores["phishing"],
            "robocall": category_scores["robocall"],
            "overall": round(overall, 1)
        }
    
    def _determine_classification(self, scores: Dict[str, float]) -> str:
        """Determine final classification based on scores"""
        if scores["overall"] < 30:
            return "safe"
        
        # Find highest category score
        category_scores = {
            "spam": scores["spam"],
            "fraud": scores["fraud"],
            "phishing": scores["phishing"],
            "robocall": scores["robocall"]
        }
        
        max_category = max(category_scores, key=lambda k: category_scores[k])
        max_score = category_scores[max_category]
        
        # Apply thresholds
        thresholds = {
            "spam": 0.4,
            "fraud": 0.5,
            "phishing": 0.45,
            "robocall": 0.5
        }
        
        if max_score >= thresholds[max_category]:
            return max_category
        
        if scores["overall"] >= 50:
            return "spam"  # Default to spam for moderate risk
        
        return "safe"
    
    def _generate_explanation(self, signals: List[FraudSignal], 
                             scores: Dict[str, float], 
                             classification: str) -> str:
        """Generate human-readable explanation"""
        if not signals:
            return "No suspicious indicators detected. The call appears to be safe."
        
        explanation_parts = []
        
        # Overall assessment
        risk_level = "high" if scores["overall"] >= 70 else "moderate" if scores["overall"] >= 40 else "low"
        explanation_parts.append(
            f"This call has been classified as {classification.upper()} with a {risk_level} risk score of {scores['overall']:.0f}/100."
        )
        
        # Key findings
        key_signals = sorted(signals, key=lambda x: x.confidence * x.weight, reverse=True)[:3]
        
        if key_signals:
            explanation_parts.append("\nKey findings:")
            for signal in key_signals:
                explanation_parts.append(f"• {signal.description}")
        
        # Recommendations
        if classification != "safe":
            explanation_parts.append("\nRecommendation: Exercise caution. Do not share personal or financial information.")
        
        return " ".join(explanation_parts)
    
    def _extract_highlights(self, text: str, signals: List[FraudSignal]) -> List[Dict]:
        """Extract phrases to highlight in the transcript"""
        highlights = []
        text_lower = text.lower()
        
        for signal in signals:
            for evidence in signal.evidence:
                if isinstance(evidence, str):
                    # Find position in text
                    pos = text_lower.find(evidence.lower())
                    if pos != -1:
                        highlights.append({
                            "text": evidence,
                            "start": pos,
                            "end": pos + len(evidence),
                            "category": signal.category,
                            "severity": "high" if signal.confidence > 0.8 else "medium"
                        })
        
        return highlights
    
    def _extract_keywords(self, signals: List[FraudSignal]) -> List[str]:
        """Extract unique suspicious keywords"""
        keywords = set()
        for signal in signals:
            if signal.signal_type == "keyword":
                keywords.update(signal.evidence)
        return list(keywords)
    
    def _extract_indicators(self, signals: List[FraudSignal]) -> List[Dict]:
        """Extract fraud indicators for display"""
        indicators = []
        seen = set()
        
        for signal in signals:
            key = (signal.signal_type, signal.category)
            if key not in seen:
                seen.add(key)
                indicators.append({
                    "type": signal.signal_type,
                    "category": signal.category,
                    "description": signal.description,
                    "severity": "high" if signal.confidence > 0.8 else "medium" if signal.confidence > 0.5 else "low"
                })
        
        return indicators
    
    def _calculate_confidence(self, signals: List[FraudSignal], scores: Dict[str, float]) -> float:
        """Calculate overall confidence in the analysis"""
        if not signals:
            return 0.95  # High confidence it's safe
        
        # Average confidence of all signals
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        # Boost confidence with more signals
        signal_boost = min(len(signals) / 10, 0.2)
        
        return min(avg_confidence + signal_boost, 0.99)
