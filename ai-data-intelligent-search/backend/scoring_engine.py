import re
from typing import List, Dict, Tuple
from models import Person, Company, ScoreBreakdown, SearchResult
from collections import Counter


class ScoringEngine:
    """Smart Recommendation & Scoring Engine"""
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize scoring engine with weights
        Default weights sum to 1.0
        """
        self.weights = weights or {
            'industry_alignment': 0.30,
            'role_relevance': 0.25,
            'location_proximity': 0.15,
            'profile_completeness': 0.10,
            'gender_match': 0.10,  # Gender matching boost
            'recency_freshness': 0.05,
            'special_flags': 0.05
        }
        # Normalize weights
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v/total for k, v in self.weights.items()}
    
    def update_weights(self, weights: Dict[str, float]):
        """Update scoring weights"""
        self.weights = weights
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v/total for k, v in self.weights.items()}
    
    def calculate_industry_alignment(self, person: Person, query_terms: List[str], company: Company = None) -> float:
        """Calculate industry alignment score (0-100)"""
        score = 0.0
        max_score = 0.0
        
        # Match person's industry with query terms
        if person.industry:
            industry_lower = person.industry.lower()
            for term in query_terms:
                term_lower = term.lower()
                max_score += 50
                if term_lower in industry_lower or industry_lower in term_lower:
                    score += 50
                elif any(word in industry_lower for word in term_lower.split() if len(word) > 3):
                    score += 30
        
        # Match with company industry if provided
        if company and company.industry:
            company_industry = company.industry.lower()
            if person.industry and person.industry.lower() in company_industry:
                score += 30
                max_score += 30
        
        return min(100, (score / max_score * 100) if max_score > 0 else 0)
    
    def calculate_role_relevance(self, person: Person, query_terms: List[str], 
                                 seniority_levels: List[str] = None) -> float:
        """Calculate role relevance score (0-100)"""
        score = 0.0
        max_score = 0.0
        
        # Check job title
        if person.job_title:
            title_lower = person.job_title.lower()
            for term in query_terms:
                term_lower = term.lower()
                max_score += 30
                if term_lower in title_lower:
                    score += 30
                elif any(word in title_lower for word in term_lower.split() if len(word) > 3):
                    score += 20
        
        # Check headline
        if person.headline:
            headline_lower = person.headline.lower()
            for term in query_terms:
                term_lower = term.lower()
                max_score += 20
                if term_lower in headline_lower:
                    score += 20
                elif any(word in headline_lower for word in term_lower.split() if len(word) > 3):
                    score += 10
        
        # Check seniority - enhanced with parsed seniority_levels
        seniority_keywords = ['ceo', 'cto', 'cio', 'cdo', 'director', 'manager', 'lead', 'senior', 
                            'principal', 'founder', 'executive', 'vp', 'vice president', 'head']
        
        # Use parsed seniority_levels if provided
        if seniority_levels:
            max_score += 40
            person_seniority = (person.seniority or "").lower()
            person_title = (person.job_title or "").lower()
            person_headline = (person.headline or "").lower()
            person_text = f"{person_seniority} {person_title} {person_headline}".lower()
            
            for level in seniority_levels:
                level_lower = level.lower()
                # Exact match
                if level_lower in person_text:
                    score += 40
                    break
                # Check for related keywords
                for keyword in seniority_keywords:
                    if keyword in level_lower and keyword in person_text:
                        score += 30
                        break
        else:
            # Fallback to query terms
            query_seniority = [term for term in query_terms if any(sk in term.lower() for sk in seniority_keywords)]
            if query_seniority and person.seniority:
                max_score += 30
                person_seniority = person.seniority.lower()
                if any(sk in person_seniority for sk in seniority_keywords):
                    score += 30
        
        return min(100, (score / max_score * 100) if max_score > 0 else 0)
    
    def calculate_location_proximity(self, person: Person, query_location: str = None) -> float:
        """Calculate location proximity score (0-100)"""
        if not query_location:
            return 50  # Neutral score if no location specified
        
        if not person.location:
            return 0
        
        query_location_lower = query_location.lower()
        person_location_lower = person.location.lower()
        
        # Exact match
        if query_location_lower == person_location_lower:
            return 100
        
        # City match
        query_city = query_location_lower.split(',')[0].strip()
        person_city = person_location_lower.split(',')[0].strip()
        if query_city == person_city:
            return 90
        
        # Partial match
        if query_city in person_location_lower or person_city in query_location_lower:
            return 70
        
        # Country match
        query_parts = query_location_lower.split(',')
        person_parts = person_location_lower.split(',')
        if len(query_parts) > 1 and len(person_parts) > 1:
            if query_parts[-1].strip() == person_parts[-1].strip():
                return 50
        
        return 0
    
    def calculate_completeness_score(self, person: Person) -> float:
        """Calculate profile completeness score (0-100)"""
        return person.profile_completeness
    
    def calculate_recency_score(self, person: Person) -> float:
        """Calculate recency/freshness score (0-100) based on importDate"""
        if not person.importDate:
            return 50  # Neutral score if no date
        
        try:
            from datetime import datetime
            # Parse import date (assuming format like "2024-01-15" or similar)
            import_date = datetime.strptime(person.importDate[:10], "%Y-%m-%d")
            days_old = (datetime.now() - import_date).days
            
            # Score decreases with age: 100 for <30 days, 75 for <90 days, 50 for <180 days, 25 for <365 days
            if days_old < 30:
                return 100
            elif days_old < 90:
                return 75
            elif days_old < 180:
                return 50
            elif days_old < 365:
                return 25
            else:
                return 10
        except:
            return 50  # Neutral if parsing fails
    
    def calculate_gender_match_score(self, person: Person, query_gender: str = None) -> float:
        """Calculate gender match score (0-100) - high boost for exact matches"""
        if not query_gender:
            return 50  # Neutral score if no gender specified
        
        if not person.gender:
            return 0  # No score if person has no gender data
        
        # Gender normalization mapping
        gender_normalization = {
            'f': 'female', 'female': 'female', 'females': 'female',
            'm': 'male', 'male': 'male', 'males': 'male'
        }
        
        query_gender_normalized = gender_normalization.get(query_gender.lower().strip(), query_gender.lower().strip())
        person_gender = str(person.gender).lower().strip()
        person_gender_normalized = gender_normalization.get(person_gender, person_gender)
        
        # Exact match gets high score
        if person_gender_normalized == query_gender_normalized:
            return 100
        
        # No match
        return 0
    
    def calculate_special_flags_score(self, person: Person) -> float:
        """Calculate score based on special flags (premium, jobSeeker)"""
        score = 50  # Base score
        
        if person.premium and str(person.premium).lower() in ['true', 'yes', '1']:
            score += 30
        
        if person.jobSeeker and str(person.jobSeeker).lower() in ['true', 'yes', '1']:
            score += 20
        
        return min(100, score)
    
    def calculate_total_score(self, person: Person, query_terms: List[str], 
                             query_location: str = None, company: Company = None,
                             seniority_levels: List[str] = None, query_gender: str = None) -> Tuple[float, ScoreBreakdown]:
        """Calculate total relevance score and breakdown (0-100 scale)"""
        industry_score = self.calculate_industry_alignment(person, query_terms, company)
        role_score = self.calculate_role_relevance(person, query_terms, seniority_levels)
        location_score = self.calculate_location_proximity(person, query_location)
        completeness_score = self.calculate_completeness_score(person)
        gender_score = self.calculate_gender_match_score(person, query_gender)
        recency_score = self.calculate_recency_score(person)
        flags_score = self.calculate_special_flags_score(person)
        
        total_score = (
            industry_score * self.weights['industry_alignment'] +
            role_score * self.weights['role_relevance'] +
            location_score * self.weights['location_proximity'] +
            completeness_score * self.weights['profile_completeness'] +
            gender_score * self.weights.get('gender_match', 0.0) +
            recency_score * self.weights['recency_freshness'] +
            flags_score * self.weights['special_flags']
        )
        
        # Ensure score is in 0-100 range
        total_score = max(0, min(100, total_score))
        
        breakdown = ScoreBreakdown(
            industry_alignment=round(industry_score, 2),
            role_relevance=round(role_score, 2),
            location_proximity=round(location_score, 2),
            profile_completeness=round(completeness_score, 2),
            total_score=round(total_score, 2)
        )
        
        return total_score, breakdown
    
    def calculate_top5_score(self, person: Person, query_terms: List[str], 
                            query_location: str = None, company: Company = None,
                            seniority_levels: List[str] = None, rank: int = 1,
                            query_gender: str = None) -> Tuple[float, ScoreBreakdown]:
        """
        Enhanced scoring formula for top 5 results with rank-based boosting
        
        Formula for top 5:
        - Base score (weighted components)
        - Rank boost: Top result gets +15%, 2nd gets +10%, 3rd gets +5%, 4th-5th get +2%
        - Seniority match boost: +10% if seniority matches
        - Profile completeness boost: +5% if >80% complete
        - Premium boost: +3% if premium member
        
        Args:
            rank: Position in results (1-5)
        """
        # Calculate base score
        base_score, breakdown = self.calculate_total_score(
            person, query_terms, query_location, company, seniority_levels, query_gender
        )
        
        # Rank-based boost (only for top 5)
        rank_boost = 0.0
        if rank == 1:
            rank_boost = 15.0
        elif rank == 2:
            rank_boost = 10.0
        elif rank == 3:
            rank_boost = 5.0
        elif rank in [4, 5]:
            rank_boost = 2.0
        
        # Seniority match boost
        seniority_boost = 0.0
        if seniority_levels and person.seniority:
            person_seniority = person.seniority.lower()
            person_title = (person.job_title or "").lower()
            person_text = f"{person_seniority} {person_title}".lower()
            
            for level in seniority_levels:
                if level.lower() in person_text:
                    seniority_boost = 10.0
                    break
        
        # Profile completeness boost
        completeness_boost = 0.0
        if person.profile_completeness > 80:
            completeness_boost = 5.0
        
        # Premium boost
        premium_boost = 0.0
        if person.premium and str(person.premium).lower() in ['true', 'yes', '1']:
            premium_boost = 3.0
        
        # Calculate final score with boosts
        final_score = base_score + rank_boost + seniority_boost + completeness_boost + premium_boost
        
        # Cap at 100
        final_score = min(100.0, final_score)
        
        # Update breakdown with final score
        breakdown.total_score = round(final_score, 2)
        
        return final_score, breakdown
    
    def generate_explanation(self, person: Person, breakdown: ScoreBreakdown, 
                            query_terms: List[str], query_location: str = None) -> str:
        """Generate explanation for why this person was matched (max 80 words)"""
        reasons = []
        
        if breakdown.industry_alignment > 50:
            reasons.append(f"Strong industry alignment ({person.industry or 'industry'})")
        
        if breakdown.role_relevance > 50:
            reasons.append(f"Relevant role ({person.job_title or 'position'})")
        
        if query_location and breakdown.location_proximity > 50:
            reasons.append(f"Based in {person.location or 'target location'}")
        
        if breakdown.profile_completeness > 70:
            reasons.append("Complete profile")
        
        if person.headline:
            headline_preview = person.headline[:50] + "..." if len(person.headline) > 50 else person.headline
            reasons.append(f"Profile: {headline_preview}")
        
        explanation = ". ".join(reasons[:3])  # Limit to top 3 reasons
        if len(explanation) > 80:
            explanation = explanation[:77] + "..."
        
        return explanation if explanation else "Matched based on profile attributes."



