"""
Roadmap.sh API Integration Service
Fetches learning paths from roadmap.sh or uses mock data
"""
import httpx
import json
from typing import Dict, List, Optional
import os

ROADMAP_SH_BASE_URL = "https://roadmap.sh"


class RoadmapService:
    """Service to fetch and manage roadmaps from roadmap.sh"""
    
    def __init__(self):
        self.base_url = ROADMAP_SH_BASE_URL
        self.use_mock = os.getenv("USE_MOCK_ROADMAP", "false").lower() == "true"
    
    async def get_roadmap(self, roadmap_slug: str) -> Optional[Dict]:
        """
        Fetch roadmap from roadmap.sh API
        
        Args:
            roadmap_slug: Slug of the roadmap (e.g., 'backend', 'frontend', 'devops')
        
        Returns:
            Roadmap data as dictionary or None if not found
        """
        if self.use_mock:
            return self._get_mock_roadmap(roadmap_slug)
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to fetch from roadmap.sh API
                # Note: roadmap.sh may not have a public API, so we'll use mock
                response = await client.get(f"{self.base_url}/{roadmap_slug}")
                if response.status_code == 200:
                    # Parse if it's JSON, otherwise return mock
                    try:
                        return response.json()
                    except:
                        return self._get_mock_roadmap(roadmap_slug)
                else:
                    return self._get_mock_roadmap(roadmap_slug)
        except Exception as e:
            print(f"Error fetching roadmap from API: {e}")
            return self._get_mock_roadmap(roadmap_slug)
    
    def _get_mock_roadmap(self, roadmap_slug: str) -> Dict:
        """
        Generate mock roadmap data similar to roadmap.sh structure
        
        Args:
            roadmap_slug: Slug of the roadmap
        
        Returns:
            Mock roadmap data
        """
        roadmaps = {
            "backend": {
                "title": "Backend Developer",
                "description": "Step by step guide to becoming a modern backend developer",
                "slug": "backend",
                "milestones": [
                    {
                        "id": 1,
                        "title": "Internet",
                        "description": "How does the internet work?",
                        "topics": [
                            {"title": "What is HTTP?", "resources": ["https://developer.mozilla.org/en-US/docs/Web/HTTP"]},
                            {"title": "DNS and how it works", "resources": ["https://www.cloudflare.com/learning/dns/what-is-dns/"]},
                            {"title": "What is Domain Name?", "resources": []}
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Basic Frontend Knowledge",
                        "description": "HTML, CSS, JavaScript basics",
                        "topics": [
                            {"title": "HTML Basics", "resources": ["https://developer.mozilla.org/en-US/docs/Web/HTML"]},
                            {"title": "CSS Basics", "resources": ["https://developer.mozilla.org/en-US/docs/Web/CSS"]},
                            {"title": "JavaScript Basics", "resources": ["https://developer.mozilla.org/en-US/docs/Web/JavaScript"]}
                        ]
                    },
                    {
                        "id": 3,
                        "title": "OS and General Knowledge",
                        "description": "Operating systems fundamentals",
                        "topics": [
                            {"title": "Terminal Usage", "resources": []},
                            {"title": "Process Management", "resources": []},
                            {"title": "Memory Management", "resources": []}
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Learn a Language",
                        "description": "Choose a backend language",
                        "topics": [
                            {"title": "Python", "resources": ["https://www.python.org/"]},
                            {"title": "Node.js", "resources": ["https://nodejs.org/"]},
                            {"title": "Java", "resources": ["https://www.java.com/"]},
                            {"title": "Go", "resources": ["https://go.dev/"]}
                        ]
                    },
                    {
                        "id": 5,
                        "title": "Version Control",
                        "description": "Git and version control",
                        "topics": [
                            {"title": "Git Basics", "resources": ["https://git-scm.com/"]},
                            {"title": "GitHub/GitLab", "resources": []}
                        ]
                    },
                    {
                        "id": 6,
                        "title": "Relational Databases",
                        "description": "SQL and relational databases",
                        "topics": [
                            {"title": "PostgreSQL", "resources": ["https://www.postgresql.org/"]},
                            {"title": "MySQL", "resources": ["https://www.mysql.com/"]},
                            {"title": "Database Design", "resources": []}
                        ]
                    },
                    {
                        "id": 7,
                        "title": "APIs",
                        "description": "REST, GraphQL, etc.",
                        "topics": [
                            {"title": "REST API", "resources": []},
                            {"title": "GraphQL", "resources": ["https://graphql.org/"]},
                            {"title": "API Design", "resources": []}
                        ]
                    },
                    {
                        "id": 8,
                        "title": "Caching",
                        "description": "Redis, Memcached",
                        "topics": [
                            {"title": "Redis", "resources": ["https://redis.io/"]},
                            {"title": "Caching Strategies", "resources": []}
                        ]
                    },
                    {
                        "id": 9,
                        "title": "Web Security",
                        "description": "Security best practices",
                        "topics": [
                            {"title": "HTTPS", "resources": []},
                            {"title": "Authentication", "resources": []},
                            {"title": "OWASP", "resources": ["https://owasp.org/"]}
                        ]
                    },
                    {
                        "id": 10,
                        "title": "Testing",
                        "description": "Unit, Integration, E2E testing",
                        "topics": [
                            {"title": "Unit Testing", "resources": []},
                            {"title": "Integration Testing", "resources": []},
                            {"title": "Test Coverage", "resources": []}
                        ]
                    }
                ]
            },
            "frontend": {
                "title": "Frontend Developer",
                "description": "Step by step guide to becoming a modern frontend developer",
                "slug": "frontend",
                "milestones": [
                    {
                        "id": 1,
                        "title": "HTML",
                        "description": "Learn HTML fundamentals",
                        "topics": [
                            {"title": "HTML Basics", "resources": []},
                            {"title": "Semantic HTML", "resources": []},
                            {"title": "Forms and Validation", "resources": []}
                        ]
                    },
                    {
                        "id": 2,
                        "title": "CSS",
                        "description": "Learn CSS styling",
                        "topics": [
                            {"title": "CSS Basics", "resources": []},
                            {"title": "Flexbox", "resources": []},
                            {"title": "Grid", "resources": []},
                            {"title": "Responsive Design", "resources": []}
                        ]
                    },
                    {
                        "id": 3,
                        "title": "JavaScript",
                        "description": "Learn JavaScript",
                        "topics": [
                            {"title": "JavaScript Basics", "resources": []},
                            {"title": "DOM Manipulation", "resources": []},
                            {"title": "Async/Await", "resources": []},
                            {"title": "ES6+ Features", "resources": []}
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Version Control",
                        "description": "Git basics",
                        "topics": [
                            {"title": "Git Basics", "resources": []}
                        ]
                    },
                    {
                        "id": 5,
                        "title": "Package Managers",
                        "description": "npm, yarn",
                        "topics": [
                            {"title": "npm", "resources": []},
                            {"title": "yarn", "resources": []}
                        ]
                    },
                    {
                        "id": 6,
                        "title": "Build Tools",
                        "description": "Webpack, Vite, etc.",
                        "topics": [
                            {"title": "Webpack", "resources": []},
                            {"title": "Vite", "resources": []}
                        ]
                    },
                    {
                        "id": 7,
                        "title": "Pick a Framework",
                        "description": "React, Vue, Angular",
                        "topics": [
                            {"title": "React", "resources": ["https://react.dev/"]},
                            {"title": "Vue", "resources": ["https://vuejs.org/"]},
                            {"title": "Angular", "resources": ["https://angular.io/"]}
                        ]
                    },
                    {
                        "id": 8,
                        "title": "State Management",
                        "description": "Redux, Zustand, etc.",
                        "topics": [
                            {"title": "Redux", "resources": []},
                            {"title": "Context API", "resources": []}
                        ]
                    },
                    {
                        "id": 9,
                        "title": "Testing",
                        "description": "Jest, React Testing Library",
                        "topics": [
                            {"title": "Jest", "resources": []},
                            {"title": "React Testing Library", "resources": []}
                        ]
                    }
                ]
            },
            "devops": {
                "title": "DevOps Engineer",
                "description": "Step by step guide to becoming a DevOps engineer",
                "slug": "devops",
                "milestones": [
                    {
                        "id": 1,
                        "title": "Learn a Programming Language",
                        "description": "Python, Go, or Bash",
                        "topics": [
                            {"title": "Python", "resources": []},
                            {"title": "Bash Scripting", "resources": []}
                        ]
                    },
                    {
                        "id": 2,
                        "title": "OS Concepts",
                        "description": "Linux fundamentals",
                        "topics": [
                            {"title": "Linux Basics", "resources": []},
                            {"title": "Process Management", "resources": []}
                        ]
                    },
                    {
                        "id": 3,
                        "title": "Networking",
                        "description": "Networking basics",
                        "topics": [
                            {"title": "TCP/IP", "resources": []},
                            {"title": "DNS", "resources": []}
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Containers",
                        "description": "Docker, Kubernetes",
                        "topics": [
                            {"title": "Docker", "resources": ["https://www.docker.com/"]},
                            {"title": "Kubernetes", "resources": ["https://kubernetes.io/"]}
                        ]
                    },
                    {
                        "id": 5,
                        "title": "CI/CD",
                        "description": "Jenkins, GitHub Actions",
                        "topics": [
                            {"title": "GitHub Actions", "resources": []},
                            {"title": "Jenkins", "resources": []}
                        ]
                    },
                    {
                        "id": 6,
                        "title": "Cloud Platforms",
                        "description": "AWS, GCP, Azure",
                        "topics": [
                            {"title": "AWS", "resources": []},
                            {"title": "GCP", "resources": []}
                        ]
                    }
                ]
            },
            "ai": {
                "title": "AI Engineer",
                "description": "Step by step guide to becoming an AI engineer",
                "slug": "ai",
                "milestones": [
                    {
                        "id": 1,
                        "title": "Mathematics",
                        "description": "Linear Algebra, Calculus, Statistics",
                        "topics": [
                            {"title": "Linear Algebra", "resources": []},
                            {"title": "Calculus", "resources": []},
                            {"title": "Statistics", "resources": []}
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Programming",
                        "description": "Python, R",
                        "topics": [
                            {"title": "Python", "resources": []},
                            {"title": "NumPy, Pandas", "resources": []}
                        ]
                    },
                    {
                        "id": 3,
                        "title": "Machine Learning",
                        "description": "ML fundamentals",
                        "topics": [
                            {"title": "Supervised Learning", "resources": []},
                            {"title": "Unsupervised Learning", "resources": []}
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Deep Learning",
                        "description": "Neural Networks",
                        "topics": [
                            {"title": "Neural Networks", "resources": []},
                            {"title": "TensorFlow", "resources": []},
                            {"title": "PyTorch", "resources": []}
                        ]
                    }
                ]
            },
            "databases": {
                "title": "Database Administrator",
                "description": "Step by step guide to database administration",
                "slug": "databases",
                "milestones": [
                    {
                        "id": 1,
                        "title": "Relational Databases",
                        "description": "SQL, PostgreSQL, MySQL",
                        "topics": [
                            {"title": "SQL Basics", "resources": []},
                            {"title": "PostgreSQL", "resources": []},
                            {"title": "MySQL", "resources": []}
                        ]
                    },
                    {
                        "id": 2,
                        "title": "NoSQL Databases",
                        "description": "MongoDB, Redis",
                        "topics": [
                            {"title": "MongoDB", "resources": []},
                            {"title": "Redis", "resources": []}
                        ]
                    },
                    {
                        "id": 3,
                        "title": "Database Design",
                        "description": "Schema design, normalization",
                        "topics": [
                            {"title": "Normalization", "resources": []},
                            {"title": "Indexing", "resources": []}
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Performance Optimization",
                        "description": "Query optimization",
                        "topics": [
                            {"title": "Query Optimization", "resources": []},
                            {"title": "Caching", "resources": []}
                        ]
                    }
                ]
            }
        }
        
        return roadmaps.get(roadmap_slug, {
            "title": f"{roadmap_slug.title()} Developer",
            "description": f"Learning path for {roadmap_slug}",
            "slug": roadmap_slug,
            "milestones": []
        })
    
    def convert_roadmap_to_tasks(self, roadmap_data: Dict, skill_id: str) -> List[Dict]:
        """
        Convert roadmap milestones to tasks
        
        Args:
            roadmap_data: Roadmap data from roadmap.sh or mock
            skill_id: UUID of the skill
        
        Returns:
            List of task dictionaries ready for database insertion
        """
        tasks = []
        
        for milestone in roadmap_data.get("milestones", []):
            milestone_num = milestone.get("id", 0)
            
            # Create milestone task
            tasks.append({
                "skill_id": skill_id,
                "title": f"Milestone {milestone_num}: {milestone.get('title', '')}",
                "description": milestone.get("description", ""),
                "task_type": "milestone",
                "difficulty": "intermediate",
                "estimated_duration_minutes": 480,  # 8 hours
                "points_reward": 100,
                "milestone_number": milestone_num,
                "order_index": milestone_num
            })
            
            # Create tasks for each topic
            for idx, topic in enumerate(milestone.get("topics", []), 1):
                tasks.append({
                    "skill_id": skill_id,
                    "title": topic.get("title", ""),
                    "description": f"Learn about {topic.get('title', '')}",
                    "task_type": "theory",
                    "difficulty": "beginner",
                    "estimated_duration_minutes": 60,
                    "points_reward": 20,
                    "milestone_number": milestone_num,
                    "order_index": milestone_num * 100 + idx,
                    "prerequisites": [] if idx == 1 else [tasks[-1]["title"]]  # Simple prerequisite logic
                })
        
        return tasks

