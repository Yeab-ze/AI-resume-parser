"""
Test script to verify OpenRouter API connectivity and resume parsing.
Run this before deploying to ensure everything works.
"""

import os
import json
from resumeparser import _load_api_key, ats_extractor

# Sample resume text for testing
SAMPLE_RESUME = """
JOHN ANDERSON
john.anderson@email.com | (555) 123-4567
linkedin.com/in/johnanderson | github.com/johnanderson

PROFESSIONAL SUMMARY
Senior Software Engineer with 8+ years of experience developing scalable web applications.
Expertise in Python, JavaScript, and cloud technologies. Proven track record of leading teams
and delivering high-impact projects.

EXPERIENCE

Senior Software Engineer | TechCorp Inc. | Jan 2021 - Present
• Led development of microservices architecture serving 10M+ daily users
• Mentored team of 5 junior developers, improving code quality by 40%
• Implemented CI/CD pipeline reducing deployment time by 60%
• Tech Stack: Python, FastAPI, PostgreSQL, AWS, Docker, Kubernetes

Software Engineer | DataFlow Systems | Jun 2018 - Dec 2020
• Developed REST APIs and backend services handling 1M+ requests/day
• Optimized database queries improving performance by 45%
• Implemented real-time data processing using Apache Kafka
• Tech Stack: Node.js, Python, MongoDB, Redis, Docker

Junior Developer | StartupLab | Jan 2017 - May 2018
• Built responsive web applications using React and Vue.js
• Collaborated with product team to implement new features
• Tech Stack: JavaScript, React, Node.js, MySQL

EDUCATION
B.S. in Computer Science | State University | 2016
Relevant Coursework: Algorithms, Database Design, Software Engineering

TECHNICAL SKILLS
Languages: Python, JavaScript, Java, SQL, Bash
Frameworks: FastAPI, Flask, Express.js, React, Vue.js
Databases: PostgreSQL, MongoDB, Redis, MySQL
Cloud: AWS (EC2, S3, Lambda), Google Cloud Platform, Docker, Kubernetes
Tools: Git, Jenkins, GitHub Actions, JIRA, Linux

SOFT SKILLS
• Team Leadership
• Project Management
• Problem Solving
• Communication
• Agile/Scrum

CERTIFICATIONS
AWS Solutions Architect Associate | 2022
Google Cloud Associate Cloud Engineer | 2021
"""

# Sample job description for matching
SAMPLE_JD = """
We are looking for a Senior Backend Engineer to join our team.

Requirements:
• 5+ years of backend development experience
• Strong Python and SQL skills
• Experience with microservices and cloud platforms
• Knowledge of containerization (Docker, Kubernetes)
• Experience with CI/CD pipelines
• Excellent problem-solving skills
• Team player with strong communication

Nice to have:
• Experience with Apache Kafka or message queues
• AWS or GCP certification
• Open source contributions
• SCRUM experience
"""


def test_api_key_loading():
    """Test if API key can be loaded."""
    print("=" * 60)
    print("TEST 1: API Key Loading")
    print("=" * 60)
    
    api_key = _load_api_key()
    
    if api_key:
        # Show masked key for security
        masked_key = api_key[:10] + "*" * (len(api_key) - 20) + api_key[-10:]
        print(f"✅ API Key loaded: {masked_key}")
        return True
    else:
        print("❌ API Key not found!")
        print("   Please set OPENROUTER_API_KEY or OPENAI_API_KEY environment variable")
        return False


def test_resume_parsing():
    """Test resume parsing without job description."""
    print("\n" + "=" * 60)
    print("TEST 2: Resume Parsing (Without JD)")
    print("=" * 60)
    
    print("Parsing sample resume...")
    result = ats_extractor(SAMPLE_RESUME)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        if "detail" in result:
            print(f"   Details: {result['detail']}")
        return False
    
    # Display results
    print(f"✅ Parsing successful!\n")
    print(f"Full Name: {result.get('full_name', 'N/A')}")
    print(f"Email: {result.get('email', 'N/A')}")
    print(f"ATS Score: {result.get('resume_score', 'N/A')}/100")
    print(f"Pass/Fail: {result.get('pass_fail', 'N/A')}")
    
    if result.get('technical_skills'):
        print(f"Technical Skills: {', '.join(result['technical_skills'][:5])}")
    
    if result.get('suggestions'):
        print(f"\nTop Suggestions:")
        for suggestion in result['suggestions'][:3]:
            print(f"  • {suggestion}")
    
    return True


def test_resume_with_jd():
    """Test resume parsing with job description."""
    print("\n" + "=" * 60)
    print("TEST 3: Resume Parsing (With JD Matching)")
    print("=" * 60)
    
    print("Parsing sample resume with job description...")
    result = ats_extractor(SAMPLE_RESUME, SAMPLE_JD)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    print(f"✅ Parsing successful!\n")
    print(f"ATS Score: {result.get('resume_score', 'N/A')}/100")
    
    if result.get('missing_keywords'):
        print(f"\nMissing Keywords from JD:")
        for keyword in result['missing_keywords'][:5]:
            print(f"  ❌ {keyword}")
    
    if result.get('suggestions'):
        print(f"\nSuggestions:")
        for suggestion in result['suggestions'][:3]:
            print(f"  💡 {suggestion}")
    
    return True


def test_full_output():
    """Display full JSON output."""
    print("\n" + "=" * 60)
    print("TEST 4: Full Output (Pretty Printed)")
    print("=" * 60)
    
    result = ats_extractor(SAMPLE_RESUME, SAMPLE_JD)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return False
    
    print(json.dumps(result, indent=2))
    return True


def main():
    """Run all tests."""
    print("\n" + "🚀 RESUME PARSER TEST SUITE 🚀".center(60))
    
    tests = [
        ("API Key Loading", test_api_key_loading),
        ("Resume Parsing", test_resume_parsing),
        ("Resume + JD Matching", test_resume_with_jd),
        ("Full Output", test_full_output),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Ready to deploy.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
