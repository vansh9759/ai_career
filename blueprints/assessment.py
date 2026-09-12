from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import User, SkillAssessment, AssessmentResult, VerifiedSkill
from database import db
from datetime import datetime
from services.scoring import DynamicScoringEngine
from services.crypto_passport import CryptoPassportEngine

assessment_bp = Blueprint('assessment', __name__)

# Enterprise Assessment Question Bank across 11 core tracks
ASSESSMENT_BANK = {
    "Python": {
        "title": "Python 3 & Backend Architecture Assessment",
        "category": "Programming Languages",
        "description": "Evaluates Python GIL, memory management, decorators, async/await, and list comprehensions.",
        "questions": [
            {
                "id": "py1",
                "question": "What is the primary function of Python's Global Interpreter Lock (GIL)?",
                "options": ["Allows true multi-core parallel execution", "Mutex protecting memory management in CPython from thread unsafe operations", "Compiles Python into C code at runtime", "Allocates virtual memory dynamically"],
                "correct": 1
            },
            {
                "id": "py2",
                "question": "Which decorator converts a method to operate on the class rather than an instance?",
                "options": ["@staticmethod", "@classmethod", "@property", "@abstractmethod"],
                "correct": 1
            },
            {
                "id": "py3",
                "question": "What is the average time complexity of key lookup in a CPython dictionary?",
                "options": ["O(N)", "O(log N)", "O(1)", "O(N log N)"],
                "correct": 2
            }
        ]
    },
    "C++": {
        "title": "C++ Systems & Memory Management Assessment",
        "category": "Systems Programming",
        "description": "Evaluates pointers, RAII, smart pointers (unique_ptr, shared_ptr), templates, and move semantics.",
        "questions": [
            {
                "id": "cpp1",
                "question": "Which smart pointer enforces single ownership of dynamic memory?",
                "options": ["std::shared_ptr", "std::unique_ptr", "std::weak_ptr", "std::auto_ptr"],
                "correct": 1
            },
            {
                "id": "cpp2",
                "question": "What core principle guarantees resource cleanup when an object goes out of scope?",
                "options": ["RAII (Resource Acquisition Is Initialization)", "OOP (Object-Oriented Programming)", "CRTP", "SFINAE"],
                "correct": 0
            }
        ]
    },
    "Java": {
        "title": "Java Enterprise & JVM Internals Assessment",
        "category": "Enterprise Software",
        "description": "Evaluates JVM memory management, GC algorithms, multithreading, and Spring Boot patterns.",
        "questions": [
            {
                "id": "java1",
                "question": "Which JVM memory region stores class structures, method data, and static variables in Java 8+?",
                "options": ["PermGen", "Metaspace", "Java Heap", "Native Stack"],
                "correct": 1
            },
            {
                "id": "java2",
                "question": "What keyword ensures variable changes are immediately visible across multiple thread caches?",
                "options": ["synchronized", "volatile", "transient", "final"],
                "correct": 1
            }
        ]
    },
    "JavaScript": {
        "title": "Modern JavaScript & Event Loop Assessment",
        "category": "Web Development",
        "description": "Evaluates ES6+, closures, prototypes, event loop microtasks/macrotasks, and Promises.",
        "questions": [
            {
                "id": "js1",
                "question": "Where are resolved Promise callbacks executed in the JavaScript Event Loop?",
                "options": ["Task Queue (Macrotask)", "Microtask Queue", "Render Queue", "Web Worker Queue"],
                "correct": 1
            },
            {
                "id": "js2",
                "question": "What is a Closure in JavaScript?",
                "options": ["A function bundled together with references to its surrounding lexical environment", "A method to encrypt JavaScript code", "A function that self-destructs after execution", "A mechanism for async HTTP calls"],
                "correct": 0
            }
        ]
    },
    "React": {
        "title": "React.js & State Architecture Assessment",
        "category": "Frontend Frameworks",
        "description": "Evaluates Fiber reconciler, Virtual DOM, custom hooks, useMemo, and Context API.",
        "questions": [
            {
                "id": "react1",
                "question": "Which hook memoizes expensive calculation results across re-renders?",
                "options": ["useCallback", "useMemo", "useRef", "useEffect"],
                "correct": 1
            },
            {
                "id": "react2",
                "question": "What is the main role of the React Fiber reconciler?",
                "options": ["Incremental rendering and ability to split/pause work across animation frames", "Compiling JSX into pure CSS", "Storing session storage cache", "Executing server SQL queries"],
                "correct": 0
            }
        ]
    },
    "SQL": {
        "title": "Advanced SQL Query Optimization Assessment",
        "category": "Database Systems",
        "description": "Evaluates indexing (B-Tree, Hash), EXPLAIN execution plans, subqueries, and window functions.",
        "questions": [
            {
                "id": "sql1",
                "question": "Which SQL window function ranks rows without leaving gaps in ranking numbers?",
                "options": ["RANK()", "DENSE_RANK()", "ROW_NUMBER()", "PERCENT_RANK()"],
                "correct": 1
            },
            {
                "id": "sql2",
                "question": "What type of index is most effective for range queries like `WHERE age BETWEEN 20 AND 30`?",
                "options": ["Hash Index", "B-Tree Index", "Bitmap Index", "Full-Text Index"],
                "correct": 1
            }
        ]
    },
    "DBMS": {
        "title": "Database Management Systems (DBMS) Fundamentals",
        "category": "Database Systems",
        "description": "Evaluates ACID properties, WAL logs, isolation levels, normalization, and concurrency control.",
        "questions": [
            {
                "id": "dbms1",
                "question": "Which transaction isolation level prevents Dirty Reads but permits Non-Repeatable Reads?",
                "options": ["Read Uncommitted", "Read Committed", "Repeatable Read", "Serializable"],
                "correct": 1
            },
            {
                "id": "dbms2",
                "question": "What does the 'A' in ACID stand for?",
                "options": ["Availability", "Atomicity", "Authentication", "Aggregation"],
                "correct": 1
            }
        ]
    },
    "OS": {
        "title": "Operating Systems & Virtual Memory Assessment",
        "category": "Computer Science Core",
        "description": "Evaluates process synchronization, semaphores, page replacement, thrashing, and deadlocks.",
        "questions": [
            {
                "id": "os1",
                "question": "What four conditions must hold simultaneously for a Deadlock to occur?",
                "options": ["Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait", "Paging, Segmentation, Swapping, Scheduling", "Read, Write, Execute, Delete", "Fork, Exec, Wait, Exit"],
                "correct": 0
            },
            {
                "id": "os2",
                "question": "What page replacement algorithm suffers from Belady's Anomaly?",
                "options": ["LRU (Least Recently Used)", "FIFO (First In First Out)", "Optimal Page Replacement", " LFU"],
                "correct": 1
            }
        ]
    },
    "CN": {
        "title": "Computer Networks & Security Assessment",
        "category": "Computer Science Core",
        "description": "Evaluates OSI layers, TCP/UDP protocols, TLS handshake, DNS resolution, and HTTP/2 multiplexing.",
        "questions": [
            {
                "id": "cn1",
                "question": "Which TCP mechanism prevents a fast sender from overwhelming a slow receiver?",
                "options": ["Congestion Control", "Flow Control (Sliding Window)", "Error Control", "Multiplexing"],
                "correct": 1
            },
            {
                "id": "cn2",
                "question": "What protocol upgrade allows multiple concurrent requests over a single TCP connection without head-of-line blocking?",
                "options": ["HTTP/1.1", "HTTP/2 (Multiplexing)", "FTP", "SMTP"],
                "correct": 1
            }
        ]
    },
    "DSA": {
        "title": "Data Structures & Algorithms Assessment",
        "category": "Algorithms",
        "description": "Evaluates time/space complexities, Dynamic Programming, Graph Traversals (BFS/DFS), and Heaps.",
        "questions": [
            {
                "id": "dsa1",
                "question": "What is the tightest upper bound time complexity for searching in a Balanced Binary Search Tree (AVL / Red-Black)?",
                "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
                "correct": 1
            },
            {
                "id": "dsa2",
                "question": "Which algorithm is used to find the shortest path in a graph with non-negative edge weights?",
                "options": ["Bellman-Ford", "Dijkstra's Algorithm", "Floyd-Warshall", "Kruskal's Algorithm"],
                "correct": 1
            }
        ]
    },
    "System Design": {
        "title": "Distributed Systems & System Design Assessment",
        "category": "Architecture",
        "description": "Evaluates CAP theorem, microservices, load balancing, Redis caching strategies, and CDN edge computing.",
        "questions": [
            {
                "id": "sd1",
                "question": "According to the CAP Theorem, what two properties can a distributed data store guarantee during a network partition?",
                "options": ["Consistency & Availability (or Partition Tolerance)", "Consistency or Availability with Partition Tolerance", "Latency & Throughput", "Scalability & Fault Tolerance"],
                "correct": 1
            },
            {
                "id": "sd2",
                "question": "Which caching pattern writes data to the cache and database simultaneously?",
                "options": ["Cache-Aside", "Write-Through", "Write-Behind (Write-Back)", "Refresh-Ahead"],
                "correct": 1
            }
        ]
    }
}

@assessment_bp.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to take skill assessments.", "warning")
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    history = AssessmentResult.query.filter_by(user_id=user_id).order_by(AssessmentResult.completed_at.desc()).all()
    
    return render_template('assessment/index.html', user=user, tracks=ASSESSMENT_BANK, history=history)

@assessment_bp.route('/take/<track_id>', methods=['GET', 'POST'])
def take(track_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to take the assessment.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    track = ASSESSMENT_BANK.get(track_id)
    if not track:
        flash(f"Assessment track '{track_id}' not found.", "danger")
        return redirect(url_for('assessment.index'))

    if request.method == 'POST':
        user_answers = request.form
        correct_count = 0
        total_questions = len(track['questions'])

        for idx, q in enumerate(track['questions']):
            ans_str = user_answers.get(f'q_{idx}')
            if ans_str is not None and int(ans_str) == q['correct']:
                correct_count += 1

        score_pct = round((correct_count / max(1, total_questions)) * 100)
        passed = score_pct >= 70

        # Save result to DB
        res = AssessmentResult(
            user_id=user_id,
            assessment_name=track['title'],
            score=score_pct,
            passed=passed,
            created_at=datetime.utcnow()
        )
        db.session.add(res)

        # If passed, issue verified skill credential
        badge_code = None
        if passed:
            cred_payload = CryptoPassportEngine.generate_credential(user_id, track_id, score=score_pct)
            badge_code = cred_payload['credential_id']
            existing_skill = VerifiedSkill.query.filter_by(user_id=user_id, skill_name=track_id).first()
            if not existing_skill:
                v_skill = VerifiedSkill(
                    user_id=user_id,
                    skill_name=track_id,
                    proficiency="Verified Proctored Expert",
                    status="Verified",
                    badge_code=badge_code
                )
                db.session.add(v_skill)
            else:
                existing_skill.badge_code = badge_code
                existing_skill.status = "Verified"

        db.session.commit()
        DynamicScoringEngine.update_user_score(user_id)

        if passed:
            flash(f"🎉 Assessment Passed with {score_pct}%! Your Cryptographic Skill Credential is issued.", "success")
        else:
            flash(f"Assessment score: {score_pct}%. You need 70% to pass and issue a skill credential.", "warning")

        return render_template(
            'assessment/result.html',
            user=user,
            track=track,
            score_pct=score_pct,
            passed=passed,
            correct_count=correct_count,
            total=total_questions,
            badge_code=badge_code
        )

    return render_template('assessment/take.html', user=user, track=track, track_id=track_id)
