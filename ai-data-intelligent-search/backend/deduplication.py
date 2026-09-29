"""
Data Deduplication Module
Phase 2: Deduplication with fuzzy matching

Detects and merges duplicate person records based on:
- Exact match on linkedinUrl/salesNavigatorId
- Fuzzy match on name + company + headline
"""

from typing import List, Dict, Set, Tuple
from rapidfuzz import fuzz
from models import Person


class DeduplicationEngine:
    """
    Deduplication engine for people records
    Uses exact matching on IDs and fuzzy matching on attributes
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize deduplication engine
        
        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider duplicates
        """
        self.similarity_threshold = similarity_threshold
    
    def normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""
        return name.lower().strip()
    
    def normalize_linkedin_url(self, url: str) -> str:
        """Normalize LinkedIn URL for comparison"""
        if not url:
            return ""
        # Extract LinkedIn profile identifier
        url_lower = url.lower().strip()
        if "linkedin.com/in/" in url_lower:
            # Extract profile slug
            parts = url_lower.split("linkedin.com/in/")
            if len(parts) > 1:
                profile = parts[1].split("/")[0].split("?")[0]
                return profile.strip()
        return url_lower
    
    def exact_match_on_ids(self, person1: Person, person2: Person) -> bool:
        """Check if two persons match exactly on IDs"""
        # Match on LinkedIn URL
        if person1.linkedinUrl and person2.linkedinUrl:
            url1 = self.normalize_linkedin_url(person1.linkedinUrl)
            url2 = self.normalize_linkedin_url(person2.linkedinUrl)
            if url1 and url2 and url1 == url2:
                return True
        
        # Match on salesNavigatorId
        if person1.salesNavigatorId and person2.salesNavigatorId:
            if person1.salesNavigatorId == person2.salesNavigatorId:
                return True
        
        return False
    
    def fuzzy_match_on_attributes(self, person1: Person, person2: Person) -> Tuple[bool, float]:
        """
        Check if two persons match based on fuzzy similarity of attributes
        
        Returns:
            (is_match, similarity_score)
        """
        # Build attribute strings
        name1 = f"{person1.firstName} {person1.lastName}".strip().lower()
        name2 = f"{person2.firstName} {person2.lastName}".strip().lower()
        
        company1 = (person1.current_company or "").lower().strip()
        company2 = (person2.current_company or "").lower().strip()
        
        headline1 = (person1.headline or "").lower().strip()
        headline2 = (person2.headline or "").lower().strip()
        
        # Calculate name similarity
        name_similarity = fuzz.ratio(name1, name2) / 100.0
        
        # Calculate company similarity
        company_similarity = 0.0
        if company1 and company2:
            company_similarity = fuzz.ratio(company1, company2) / 100.0
        
        # Calculate headline similarity
        headline_similarity = 0.0
        if headline1 and headline2:
            headline_similarity = fuzz.ratio(headline1, headline2) / 100.0
        
        # Weighted combination: name is most important
        combined_similarity = (
            name_similarity * 0.5 +
            company_similarity * 0.3 +
            headline_similarity * 0.2
        )
        
        # Consider match if combined similarity exceeds threshold
        is_match = combined_similarity >= self.similarity_threshold
        
        return is_match, combined_similarity
    
    def deduplicate_optimized(self, people: List[Person]) -> Tuple[List[Person], Dict[str, List[str]]]:
        """
        Optimized deduplication algorithm using hash-based lookups
        Much faster for large datasets (O(n) for exact matches, O(n*m) for fuzzy where m << n)
        
        Returns:
            (deduplicated_people, merge_map)
            where merge_map[kept_id] = [merged_ids]
        """
        deduplicated = []
        seen_ids: Set[str] = set()
        merge_map: Dict[str, List[str]] = {}
        
        # Hash maps for fast exact matching
        linkedin_url_map: Dict[str, Person] = {}  # normalized_url -> Person
        sales_nav_id_map: Dict[str, Person] = {}  # salesNavigatorId -> Person
        
        # For fuzzy matching candidates (group by normalized name+company for faster lookup)
        fuzzy_candidates: Dict[str, List[Person]] = {}  # normalized_key -> [Person]
        
        print(f"Processing {len(people)} records for deduplication...")
        
        for person in people:
            # Skip if already processed
            if person.id in seen_ids:
                continue
            
            # Check for exact matches using hash maps (O(1) lookup)
            exact_match_found = False
            matched_person = None
            
            # Check LinkedIn URL match
            if person.linkedinUrl:
                normalized_url = self.normalize_linkedin_url(person.linkedinUrl)
                if normalized_url and normalized_url in linkedin_url_map:
                    matched_person = linkedin_url_map[normalized_url]
                    exact_match_found = True
            
            # Check salesNavigatorId match
            if not exact_match_found and person.salesNavigatorId:
                if person.salesNavigatorId in sales_nav_id_map:
                    matched_person = sales_nav_id_map[person.salesNavigatorId]
                    exact_match_found = True
            
            if exact_match_found and matched_person:
                # Merge: keep the more complete profile
                if person.profile_completeness > matched_person.profile_completeness:
                    # Replace existing with better profile
                    deduplicated.remove(matched_person)
                    deduplicated.append(person)
                    merge_map[person.id] = merge_map.get(matched_person.id, []) + [matched_person.id]
                    if matched_person.id in merge_map:
                        del merge_map[matched_person.id]
                    
                    # Update hash maps
                    if matched_person.linkedinUrl:
                        normalized_url = self.normalize_linkedin_url(matched_person.linkedinUrl)
                        if normalized_url:
                            linkedin_url_map[normalized_url] = person
                    if matched_person.salesNavigatorId:
                        sales_nav_id_map[matched_person.salesNavigatorId] = person
                    
                    # Update fuzzy candidates
                    fuzzy_key = self._get_fuzzy_key(matched_person)
                    if fuzzy_key in fuzzy_candidates:
                        fuzzy_candidates[fuzzy_key].remove(matched_person)
                        if not fuzzy_candidates[fuzzy_key]:
                            del fuzzy_candidates[fuzzy_key]
                    fuzzy_key_new = self._get_fuzzy_key(person)
                    if fuzzy_key_new not in fuzzy_candidates:
                        fuzzy_candidates[fuzzy_key_new] = []
                    fuzzy_candidates[fuzzy_key_new].append(person)
                else:
                    # Keep existing, merge this one
                    merge_map[matched_person.id] = merge_map.get(matched_person.id, []) + [person.id]
                
                seen_ids.add(person.id)
                continue
            
            # Check for fuzzy matches (only check candidates with similar name+company)
            fuzzy_match_found = False
            fuzzy_key = self._get_fuzzy_key(person)
            
            # Check candidates with same fuzzy key
            candidates_to_check = []
            if fuzzy_key in fuzzy_candidates:
                candidates_to_check.extend(fuzzy_candidates[fuzzy_key])
            
            # Also check similar keys (for typos/variations)
            for key in fuzzy_candidates.keys():
                if key != fuzzy_key and self._keys_similar(key, fuzzy_key):
                    candidates_to_check.extend(fuzzy_candidates[key])
            
            for candidate in candidates_to_check:
                is_match, similarity = self.fuzzy_match_on_attributes(person, candidate)
                if is_match:
                    # Merge: keep the more complete profile
                    if person.profile_completeness > candidate.profile_completeness:
                        deduplicated.remove(candidate)
                        deduplicated.append(person)
                        merge_map[person.id] = merge_map.get(candidate.id, []) + [candidate.id]
                        if candidate.id in merge_map:
                            del merge_map[candidate.id]
                        
                        # Update hash maps
                        if person.linkedinUrl:
                            normalized_url = self.normalize_linkedin_url(person.linkedinUrl)
                            if normalized_url:
                                linkedin_url_map[normalized_url] = person
                        if person.salesNavigatorId:
                            sales_nav_id_map[person.salesNavigatorId] = person
                        
                        # Update fuzzy candidates
                        old_key = self._get_fuzzy_key(candidate)
                        if old_key in fuzzy_candidates:
                            fuzzy_candidates[old_key].remove(candidate)
                            if not fuzzy_candidates[old_key]:
                                del fuzzy_candidates[old_key]
                        if fuzzy_key not in fuzzy_candidates:
                            fuzzy_candidates[fuzzy_key] = []
                        fuzzy_candidates[fuzzy_key].append(person)
                    else:
                        merge_map[candidate.id] = merge_map.get(candidate.id, []) + [person.id]
                    
                    fuzzy_match_found = True
                    seen_ids.add(person.id)
                    break
            
            if not fuzzy_match_found:
                # New unique person
                deduplicated.append(person)
                seen_ids.add(person.id)
                
                # Add to hash maps for future lookups
                if person.linkedinUrl:
                    normalized_url = self.normalize_linkedin_url(person.linkedinUrl)
                    if normalized_url:
                        linkedin_url_map[normalized_url] = person
                if person.salesNavigatorId:
                    sales_nav_id_map[person.salesNavigatorId] = person
                
                # Add to fuzzy candidates
                if fuzzy_key not in fuzzy_candidates:
                    fuzzy_candidates[fuzzy_key] = []
                fuzzy_candidates[fuzzy_key].append(person)
        
        return deduplicated, merge_map
    
    def _get_fuzzy_key(self, person: Person) -> str:
        """Generate a key for fuzzy matching grouping (normalized name + company)"""
        name = f"{person.firstName} {person.lastName}".strip().lower()
        company = (person.current_company or "").lower().strip()
        # Use first 3 chars of name and company for grouping
        name_part = name[:3] if len(name) >= 3 else name
        company_part = company[:3] if len(company) >= 3 else company
        return f"{name_part}|{company_part}"
    
    def _keys_similar(self, key1: str, key2: str) -> bool:
        """Check if two fuzzy keys are similar enough to check"""
        parts1 = key1.split('|')
        parts2 = key2.split('|')
        if len(parts1) != 2 or len(parts2) != 2:
            return False
        # Check if name parts or company parts match
        return parts1[0] == parts2[0] or parts1[1] == parts2[1]
    
    def deduplicate(self, people: List[Person]) -> Tuple[List[Person], Dict[str, List[str]]]:
        """
        Deduplicate list of people
        
        Returns:
            (deduplicated_people, merge_map)
            where merge_map[kept_id] = [merged_ids]
        """
        deduplicated = []
        seen_ids: Set[str] = {}
        merge_map: Dict[str, List[str]] = {}
        
        for person in people:
            # Skip if already processed
            if person.id in seen_ids:
                continue
            
            # Check for exact matches
            exact_match_found = False
            for existing_person in deduplicated:
                if self.exact_match_on_ids(person, existing_person):
                    # Merge into existing person (keep the more complete one)
                    if person.profile_completeness > existing_person.profile_completeness:
                        # Replace existing with better profile
                        deduplicated.remove(existing_person)
                        deduplicated.append(person)
                        merge_map[person.id] = merge_map.get(existing_person.id, []) + [existing_person.id]
                        if existing_person.id in merge_map:
                            del merge_map[existing_person.id]
                    else:
                        # Keep existing, merge this one
                        merge_map[existing_person.id] = merge_map.get(existing_person.id, []) + [person.id]
                    exact_match_found = True
                    seen_ids[person.id] = True
                    break
            
            if exact_match_found:
                continue
            
            # Check for fuzzy matches
            fuzzy_match_found = False
            for existing_person in deduplicated:
                is_match, similarity = self.fuzzy_match_on_attributes(person, existing_person)
                if is_match:
                    # Merge: keep the more complete profile
                    if person.profile_completeness > existing_person.profile_completeness:
                        deduplicated.remove(existing_person)
                        deduplicated.append(person)
                        merge_map[person.id] = merge_map.get(existing_person.id, []) + [existing_person.id]
                        if existing_person.id in merge_map:
                            del merge_map[existing_person.id]
                    else:
                        merge_map[existing_person.id] = merge_map.get(existing_person.id, []) + [person.id]
                    fuzzy_match_found = True
                    seen_ids[person.id] = True
                    break
            
            if not fuzzy_match_found:
                # New unique person
                deduplicated.append(person)
                seen_ids[person.id] = True
        
        return deduplicated, merge_map
    
    def get_deduplication_stats(self, original_count: int, deduplicated_count: int) -> Dict[str, any]:
        """Get deduplication statistics"""
        removed_count = original_count - deduplicated_count
        reduction_percent = (removed_count / original_count * 100) if original_count > 0 else 0
        
        return {
            "original_count": original_count,
            "deduplicated_count": deduplicated_count,
            "removed_count": removed_count,
            "reduction_percent": round(reduction_percent, 2)
        }




