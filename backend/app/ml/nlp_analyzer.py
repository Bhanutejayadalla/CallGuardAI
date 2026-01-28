"""
NLP Analyzer
Natural Language Processing for intent detection and entity extraction
"""

from typing import Dict, List, Any, Optional
from loguru import logger
import re


class NLPAnalyzer:
    """
    NLP analysis for call transcripts
    Includes intent detection, entity extraction, and sentiment analysis
    """
    
    def __init__(self):
        self.nlp = None
        self._load_nlp()
    
    def _load_nlp(self):
        """Load spaCy NLP model"""
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, NLP features limited")
        except ImportError:
            logger.warning("spaCy not installed, NLP features limited")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive NLP analysis
        """
        return {
            "intent": self.detect_intent(text),
            "entities": self.extract_entities(text),
            "sentiment": self.analyze_sentiment(text),
            "topics": self.extract_topics(text),
            "questions": self.extract_questions(text),
            "commands": self.extract_commands(text)
        }
    
    def detect_intent(self, text: str) -> Dict[str, Any]:
        """
        Detect the intent/purpose of the call
        """
        text_lower = text.lower()
        
        # Intent patterns with confidence scores
        intent_patterns = {
            "request_money": {
                "patterns": [
                    r"send (?:me |us )?money", r"transfer funds?", r"wire transfer",
                    r"pay (?:immediately|now|today)", r"make (?:a )?payment",
                    r"deposit", r"gift card"
                ],
                "category": "fraud"
            },
            "request_info": {
                "patterns": [
                    r"(?:tell|give|share|provide) (?:me |us )?(?:your )?",
                    r"what is your", r"need your (?:information|details)",
                    r"verify your", r"confirm your"
                ],
                "category": "phishing"
            },
            "create_urgency": {
                "patterns": [
                    r"immediately", r"right now", r"urgent(?:ly)?",
                    r"(?:last|final) (?:chance|warning|notice)",
                    r"(?:limited|running out of) time", r"expires? (?:today|soon)"
                ],
                "category": "fraud"
            },
            "threaten": {
                "patterns": [
                    r"arrest", r"warrant", r"legal action", r"sue",
                    r"police", r"court", r"penalty", r"fine"
                ],
                "category": "fraud"
            },
            "offer_prize": {
                "patterns": [
                    r"(?:you(?:'ve)?|you have) won", r"congratulations",
                    r"(?:lottery|prize|reward) winner", r"claim your (?:prize|reward)",
                    r"selected (?:for|to receive)"
                ],
                "category": "spam"
            },
            "impersonate": {
                "patterns": [
                    r"(?:this is|calling from) (?:the )?(?:IRS|FBI|police|bank|microsoft|apple|amazon)",
                    r"(?:government|federal|official) (?:agency|department)",
                    r"your (?:bank|credit card company)"
                ],
                "category": "fraud"
            },
            "sell_product": {
                "patterns": [
                    r"special offer", r"limited time (?:offer|deal)",
                    r"(?:exclusive|amazing) (?:deal|discount|offer)",
                    r"(?:free|discounted) (?:trial|offer)"
                ],
                "category": "spam"
            },
            "legitimate_inquiry": {
                "patterns": [
                    r"(?:how|what|when|where|why) (?:can|do|is|are|would)",
                    r"(?:i'd like to|i want to|can i) (?:ask|know|learn)",
                    r"(?:could you|would you) (?:help|assist|tell)"
                ],
                "category": "safe"
            }
        }
        
        detected_intents = []
        
        for intent_name, intent_data in intent_patterns.items():
            for pattern in intent_data["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected_intents.append({
                        "intent": intent_name,
                        "category": intent_data["category"],
                        "pattern": pattern
                    })
                    break
        
        # Determine primary intent
        if detected_intents:
            # Prioritize by category risk
            priority = {"fraud": 3, "phishing": 2, "spam": 1, "safe": 0}
            detected_intents.sort(key=lambda x: priority.get(x["category"], 0), reverse=True)
            primary = detected_intents[0]
        else:
            primary = {"intent": "unknown", "category": "unknown"}
        
        return {
            "primary_intent": primary["intent"],
            "category": primary.get("category", "unknown"),
            "all_intents": [d["intent"] for d in detected_intents],
            "confidence": min(0.5 + len(detected_intents) * 0.1, 0.95)
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        """
        entities = []
        
        # Use spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
        
        # Custom entity extraction for sensitive data
        custom_entities = self._extract_custom_entities(text)
        entities.extend(custom_entities)
        
        return entities
    
    def _extract_custom_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract custom entities like phone numbers, SSN, etc."""
        entities = []
        
        # Phone numbers
        phone_pattern = r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b'
        for match in re.finditer(phone_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "PHONE_NUMBER",
                "start": match.start(),
                "end": match.end(),
                "sensitive": True
            })
        
        # Credit card numbers (basic pattern)
        cc_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        for match in re.finditer(cc_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "CREDIT_CARD",
                "start": match.start(),
                "end": match.end(),
                "sensitive": True
            })
        
        # SSN pattern
        ssn_pattern = r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'
        for match in re.finditer(ssn_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "SSN",
                "start": match.start(),
                "end": match.end(),
                "sensitive": True
            })
        
        # Money amounts
        money_pattern = r'\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD)\b'
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            entities.append({
                "text": match.group(),
                "type": "MONEY",
                "start": match.start(),
                "end": match.end()
            })
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "EMAIL",
                "start": match.start(),
                "end": match.end()
            })
        
        return entities
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the text
        """
        # Simple rule-based sentiment analysis
        text_lower = text.lower()
        
        positive_words = [
            "thank", "please", "appreciate", "help", "great", "good",
            "wonderful", "excellent", "happy", "glad", "sure", "yes"
        ]
        
        negative_words = [
            "urgent", "immediate", "warning", "danger", "problem", "issue",
            "suspend", "cancel", "arrest", "police", "legal", "sue",
            "angry", "frustrated", "terrible", "bad", "worst"
        ]
        
        threatening_words = [
            "arrest", "warrant", "police", "jail", "court", "sue",
            "legal action", "penalty", "fine", "prosecute"
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        threatening_count = sum(1 for word in threatening_words if word in text_lower)
        
        total = positive_count + negative_count + 1
        
        if threatening_count > 0:
            sentiment = "threatening"
            score = -0.8
        elif negative_count > positive_count:
            sentiment = "negative"
            score = -(negative_count - positive_count) / total
        elif positive_count > negative_count:
            sentiment = "positive"
            score = (positive_count - negative_count) / total
        else:
            sentiment = "neutral"
            score = 0
        
        return {
            "sentiment": sentiment,
            "score": max(min(score, 1), -1),
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "threatening_indicators": threatening_count
        }
    
    def extract_topics(self, text: str) -> List[str]:
        """
        Extract main topics from the text
        """
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            "banking": ["bank", "account", "transfer", "deposit", "withdrawal", "balance"],
            "security": ["security", "password", "verify", "authenticate", "breach", "hack"],
            "legal": ["legal", "court", "warrant", "arrest", "lawsuit", "attorney"],
            "tax": ["tax", "irs", "refund", "filing", "return", "audit"],
            "insurance": ["insurance", "policy", "claim", "coverage", "premium"],
            "tech_support": ["computer", "virus", "microsoft", "apple", "support", "tech"],
            "healthcare": ["medical", "doctor", "hospital", "insurance", "medicare"],
            "lottery": ["lottery", "prize", "winner", "jackpot", "sweepstakes"],
            "debt": ["debt", "loan", "credit", "collection", "payment"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def extract_questions(self, text: str) -> List[str]:
        """
        Extract questions from the text
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        questions = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Check if it's a question
            if sentence and (
                sentence.endswith('?') or
                re.match(r'^(?:what|where|when|why|how|who|which|can|could|would|do|does|did|is|are|was|were)\b', 
                        sentence, re.IGNORECASE)
            ):
                questions.append(sentence)
        
        return questions
    
    def extract_commands(self, text: str) -> List[Dict[str, str]]:
        """
        Extract imperative commands from the text
        """
        commands = []
        text_lower = text.lower()
        
        command_patterns = [
            (r"press (\d|one|two|three|four|five|six|seven|eight|nine|zero)", "keypad_action"),
            (r"call (?:us |me )?(?:back )?(?:at|on) ([\d\-\s]+)", "callback_request"),
            (r"(?:send|transfer|wire) (?:me |us )?(?:\$?[\d,]+|money|funds)", "money_request"),
            (r"(?:give|tell|share|provide) (?:me |us )?(?:your )?(\w+)", "info_request"),
            (r"(?:click|go to|visit) (?:the |this )?(?:link|website|url)", "link_action"),
            (r"(?:do not|don't) hang up", "stay_on_line"),
            (r"(?:verify|confirm|update) (?:your )?(?:account|information|details)", "verification_request")
        ]
        
        for pattern, command_type in command_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                commands.append({
                    "type": command_type,
                    "match": match if isinstance(match, str) else match[0] if match else "",
                    "risk_level": "high" if command_type in ["money_request", "info_request"] else "medium"
                })
        
        return commands
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text
        """
        try:
            from langdetect import detect
            return detect(text)
        except:
            # Simple heuristic for common languages
            hindi_chars = re.findall(r'[\u0900-\u097F]', text)
            if len(hindi_chars) > len(text) * 0.1:
                return "hi"
            return "en"
