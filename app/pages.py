"""

HTML page builders for SkillForge AI.

Kept in a separate module so main.py stays clean.

"""

import json

import os

import re

import urllib.parse

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL  = os.getenv("SUPABASE_URL",  "https://xgnplnjihlcszxacpkul.supabase.co")

SUPABASE_ANON = os.getenv("SUPABASE_ANON_KEY", "")

#                                                                            

# LOGIN PAGE

#                                                                            

def _build_login_html() -> str:

    head = (

        "<!DOCTYPE html>"

        "<html lang='en'>"

        "<head>"

        "<meta charset='UTF-8'>"

        "<meta name='viewport' content='width=device-width,initial-scale=1'>"

        "<title>SkillForge AI - Sign In</title>"

        "<link rel='preconnect' href='https://fonts.googleapis.com'>"

        "<link href='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700"

        "&family=Inter:wght@400;500;600&display=swap' rel='stylesheet'>"

        "<script src='https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js'></script>"

        "<script>"

        "const SUPABASE_URL  = '" + SUPABASE_URL.replace("'", "\\'") + "';"

        "const SUPABASE_ANON = '" + SUPABASE_ANON.replace("'", "\\'") + "';"

        "</script>"

    )

    style = """

<style>

*{box-sizing:border-box;margin:0;padding:0}

:root{--ink:#0B0D10;--surface:#14171C;--surface-2:#1B1F26;--line:#262B33;

  --ember:#FF8A3D;--ember-dim:#7A4420;--steel:#7C8CA6;--text:#F1F2F4;--muted:#9298A6;

  --green:#4CAF50;--red:#ef5350}

body{background:var(--ink);color:var(--text);font-family:'Inter',sans-serif;

  min-height:100vh;display:flex;flex-direction:column;align-items:center;

  justify-content:center;padding:24px;opacity:0;transition:opacity .2s ease}

body::before{content:'';position:fixed;inset:0;pointer-events:none;

  background:radial-gradient(600px 400px at 20% 20%,rgba(255,138,61,.07),transparent 60%),

             radial-gradient(500px 500px at 80% 70%,rgba(124,140,166,.05),transparent 60%)}

.brand{display:flex;align-items:center;gap:10px;font-family:'Space Grotesk',sans-serif;

  font-weight:700;font-size:22px;margin-bottom:36px;position:relative;z-index:1}

.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;

  padding:36px 32px;width:100%;max-width:420px;position:relative;z-index:1}

.tab-row{display:flex;gap:0;margin-bottom:28px;background:var(--surface-2);

  border-radius:8px;padding:4px}

.auth-tab{flex:1;padding:9px;text-align:center;border-radius:6px;font-size:14px;

  font-weight:600;cursor:pointer;color:var(--muted);transition:all .2s}

.auth-tab.active{background:var(--ink);color:var(--ember);border:1px solid var(--ember-dim)}

.form-group{margin-bottom:18px}

label{display:block;font-size:13px;color:var(--muted);margin-bottom:6px;font-weight:500}

input{width:100%;background:var(--surface-2);border:1px solid var(--line);

  border-radius:8px;padding:11px 14px;font-size:14px;color:var(--text);

  font-family:'Inter',sans-serif;outline:none;transition:border-color .2s}

input:focus{border-color:var(--ember-dim);box-shadow:0 0 0 3px rgba(255,138,61,.08)}

input::placeholder{color:#555b65}

.btn-primary{width:100%;background:var(--ember);color:#1A0E05;border:none;

  border-radius:8px;padding:12px;font-size:15px;font-weight:700;cursor:pointer;

  font-family:'Inter',sans-serif;margin-top:4px;transition:background .15s}

.btn-primary:hover{background:#ffa15e}

.btn-primary:disabled{opacity:.6;cursor:not-allowed}

.divider{display:flex;align-items:center;gap:12px;margin:20px 0;

  color:var(--muted);font-size:13px}

.divider::before,.divider::after{content:'';flex:1;height:1px;background:var(--line)}

.btn-google{width:100%;background:transparent;border:1px solid var(--line);

  color:var(--text);border-radius:8px;padding:11px;font-size:14px;font-weight:600;

  cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px;

  font-family:'Inter',sans-serif;transition:border-color .2s,background .2s}

.btn-google:hover{border-color:var(--steel);background:var(--surface-2)}

.msg{font-size:13px;padding:10px 14px;border-radius:8px;margin-top:14px;display:none}

.msg.error{background:rgba(239,83,80,.12);border:1px solid var(--red);

  color:var(--red);display:block}

.msg.success{background:rgba(76,175,80,.12);border:1px solid var(--green);

  color:var(--green);display:block}

.footer-link{text-align:center;margin-top:20px;font-size:13px;color:var(--muted)}

.footer-link a{color:var(--ember);text-decoration:none}

.password-wrap{position:relative}

.toggle-pw{position:absolute;right:12px;top:50%;transform:translateY(-50%);

  background:none;border:none;color:var(--muted);cursor:pointer;font-size:13px;padding:4px}

.strength-bar{height:4px;border-radius:2px;margin-top:6px;

  background:var(--surface-2);overflow:hidden}

.strength-fill{height:100%;border-radius:2px;width:0;transition:width .3s,background .3s}

.strength-text{font-size:11px;color:var(--muted);margin-top:4px}

h2{font-family:'Space Grotesk',sans-serif;font-size:22px;margin-bottom:4px}

.subtitle{font-size:14px;color:var(--muted);margin-bottom:24px}

</style>

</head>

"""

    body = """

<body>

<div class="brand">

  <svg width="28" height="28" viewBox="0 0 24 24" fill="none">

    <path d="M12 2L4 7v10l8 5 8-5V7l-8-5z" stroke="#FF8A3D" stroke-width="1.6"/>

    <path d="M12 8v8M8 10l4-2 4 2" stroke="#FF8A3D" stroke-width="1.6" stroke-linecap="round"/>

  </svg>

  SkillForge AI

</div>

<div class="card">

  <div class="tab-row">

    <div class="auth-tab active" id="tab-signin" onclick="switchTab('signin')">Sign In</div>

    <div class="auth-tab"        id="tab-signup" onclick="switchTab('signup')">Sign Up</div>

  </div>

  <!-- SIGN IN -->

  <div id="form-signin">

    <h2>Welcome back</h2>

    <p class="subtitle">Sign in to your SkillForge account</p>

    <div class="form-group">

      <label for="si-email">Email</label>

      <input type="email" id="si-email" placeholder="you@example.com" autocomplete="email">

    </div>

    <div class="form-group">

      <label for="si-password">Password</label>

      <div class="password-wrap">

        <input type="password" id="si-password" placeholder="Your password"

               autocomplete="current-password">

        <button class="toggle-pw" type="button" onclick="togglePw('si-password',this)">Show</button>

      </div>

    </div>

    <button class="btn-primary" id="signin-btn" onclick="handleSignIn()">Sign In</button>

    <div class="divider">or</div>

    <button class="btn-google" onclick="handleGoogle()">

      <svg width="18" height="18" viewBox="0 0 48 48">

        <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.2l6.7-6.7C35.9 2.5 30.3 0 24 0 14.8 0 6.9 5.4 3 13.3l7.8 6C12.7 13.2 17.9 9.5 24 9.5z"/>

        <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4 7.1-10 7.1-17z"/>

        <path fill="#FBBC05" d="M10.8 28.7A14.7 14.7 0 0 1 9.5 24c0-1.6.3-3.2.7-4.7l-7.8-6A23.9 23.9 0 0 0 0 24c0 3.9.9 7.6 2.6 10.8l8.2-6.1z"/>

        <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.5-5.8c-2.2 1.5-5 2.3-8.4 2.3-6.1 0-11.3-3.7-13.2-9l-8.2 6.1C6.9 42.6 14.8 48 24 48z"/>

      </svg>

      Continue with Google

    </button>

    <div class="msg" id="si-msg"></div>

  </div>

  <!-- SIGN UP -->

  <div id="form-signup" style="display:none">

    <h2>Create account</h2>

    <p class="subtitle">Start learning any topic for free</p>

    <div class="form-group">

      <label for="su-name">Full name</label>

      <input type="text" id="su-name" placeholder="Your name" autocomplete="name">

    </div>

    <div class="form-group">

      <label for="su-email">Email</label>

      <input type="email" id="su-email" placeholder="you@example.com" autocomplete="email">

    </div>

    <div class="form-group">

      <label for="su-password">Password</label>

      <div class="password-wrap">

        <input type="password" id="su-password" placeholder="Min 8 characters"

               autocomplete="new-password" oninput="checkStrength(this.value)">

        <button class="toggle-pw" type="button" onclick="togglePw('su-password',this)">Show</button>

      </div>

      <div class="strength-bar"><div class="strength-fill" id="strength-fill"></div></div>

      <div class="strength-text" id="strength-text"></div>

    </div>

    <div class="form-group">

      <label for="su-confirm">Confirm password</label>

      <div class="password-wrap">

        <input type="password" id="su-confirm" placeholder="Repeat password"

               autocomplete="new-password">

        <button class="toggle-pw" type="button" onclick="togglePw('su-confirm',this)">Show</button>

      </div>

    </div>

    <button class="btn-primary" id="signup-btn" onclick="handleSignUp()">Create Account</button>

    <div class="divider">or</div>

    <button class="btn-google" onclick="handleGoogle()">

      <svg width="18" height="18" viewBox="0 0 48 48">

        <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.2l6.7-6.7C35.9 2.5 30.3 0 24 0 14.8 0 6.9 5.4 3 13.3l7.8 6C12.7 13.2 17.9 9.5 24 9.5z"/>

        <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4 7.1-10 7.1-17z"/>

        <path fill="#FBBC05" d="M10.8 28.7A14.7 14.7 0 0 1 9.5 24c0-1.6.3-3.2.7-4.7l-7.8-6A23.9 23.9 0 0 0 0 24c0 3.9.9 7.6 2.6 10.8l8.2-6.1z"/>

        <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.5-5.8c-2.2 1.5-5 2.3-8.4 2.3-6.1 0-11.3-3.7-13.2-9l-8.2 6.1C6.9 42.6 14.8 48 24 48z"/>

      </svg>

      Continue with Google

    </button>

    <div class="msg" id="su-msg"></div>

  </div>

</div>

<div class="footer-link"><a href="/">Back to home</a></div>

"""

    script = """

<script>

function switchTab(tab) {

  var si = document.getElementById('form-signin');

  var su = document.getElementById('form-signup');

  var ts = document.getElementById('tab-signin');

  var tu = document.getElementById('tab-signup');

  si.style.display = tab === 'signin' ? 'block' : 'none';

  su.style.display = tab === 'signup' ? 'block' : 'none';

  ts.className = 'auth-tab' + (tab === 'signin' ? ' active' : '');

  tu.className = 'auth-tab' + (tab === 'signup' ? ' active' : '');

}

function togglePw(id, btn) {

  var inp = document.getElementById(id);

  var show = inp.type === 'password';

  inp.type = show ? 'text' : 'password';

  btn.textContent = show ? 'Hide' : 'Show';

}

function showMsg(id, text, type) {

  var el = document.getElementById(id);

  el.textContent = text;

  el.className = 'msg ' + type;

}

function checkStrength(pw) {

  var fill = document.getElementById('strength-fill');

  var txt  = document.getElementById('strength-text');

  var score = 0;

  if (pw.length >= 8) score++;

  if (/[A-Z]/.test(pw)) score++;

  if (/[0-9]/.test(pw)) score++;

  if (/[^A-Za-z0-9]/.test(pw)) score++;

  var colors = ['#ef5350','#FF8A3D','#ffb300','#4CAF50'];

  var labels = ['Weak','Fair','Good','Strong'];

  fill.style.width = (score * 25) + '%';

  fill.style.background = colors[score - 1] || '#ef5350';

  txt.textContent = pw.length ? (labels[score - 1] || 'Very weak') : '';

}

var _sb = (SUPABASE_URL && SUPABASE_ANON && window.supabase)

  ? window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON)

  : null;

// Read the ?next= redirect target from the URL, default to '/'

var _nextUrl = (new URLSearchParams(window.location.search)).get('next') || '/';

// Only auto-redirect when the user was bounced here from a protected page.
// If _nextUrl is '/' they came directly -- show the login form, no flash.
if (_sb && _nextUrl !== '/') {
  _sb.auth.getSession().then(function(r) {
    if (r && r.data && r.data.session && r.data.session.access_token) {
      window.location.href = _nextUrl;
    } else {
      document.body.style.opacity = '1';
    }
  });
} else {
  document.body.style.opacity = '1';
}

async function handleSignIn() {

  var email = document.getElementById('si-email').value.trim();

  var pw    = document.getElementById('si-password').value;

  var btn   = document.getElementById('signin-btn');

  if (!email || !pw) { showMsg('si-msg','Please fill in all fields.','error'); return; }

  btn.disabled = true; btn.textContent = 'Signing in...';

  if (!_sb) {

    // Demo mode -- no Supabase key yet

    setTimeout(function() {

      showMsg('si-msg','Signed in (demo mode)! Redirecting...','success');

      setTimeout(function() { window.location.href = _nextUrl; }, 800);

    }, 600);

    return;

  }

  var res = await _sb.auth.signInWithPassword({ email: email, password: pw });

  if (res.error) {

    var msg = res.error.message;

    if (msg.toLowerCase().indexOf('email') !== -1 && msg.toLowerCase().indexOf('confirm') !== -1) {

      msg = '\u2709\ufe0f Please check your email and click the confirmation link first, then sign in.';

    } else if (msg.toLowerCase().indexOf('invalid') !== -1) {

      msg = 'Incorrect email or password. Please try again.';

    }

    showMsg('si-msg', msg, 'error');

    btn.disabled = false; btn.textContent = 'Sign In';

  } else {

    showMsg('si-msg','Signed in! Redirecting...','success');

    setTimeout(function() { window.location.href = _nextUrl; }, 800);

  }

}

async function handleSignUp() {

  var name    = document.getElementById('su-name').value.trim();

  var email   = document.getElementById('su-email').value.trim();

  var pw      = document.getElementById('su-password').value;

  var confirm = document.getElementById('su-confirm').value;

  var btn     = document.getElementById('signup-btn');

  if (!name || !email || !pw || !confirm) {

    showMsg('su-msg','Please fill in all fields.','error'); return;

  }

  if (pw.length < 8) { showMsg('su-msg','Password must be at least 8 characters.','error'); return; }

  if (pw !== confirm) { showMsg('su-msg','Passwords do not match.','error'); return; }

  btn.disabled = true; btn.textContent = 'Creating account...';

  if (!_sb) {

    setTimeout(function() {

      showMsg('su-msg','Account created (demo)! Switching to sign in...','success');

      setTimeout(function() { switchTab('signin'); btn.disabled=false; btn.textContent='Create Account'; }, 1500);

    }, 600);

    return;

  }

  var res = await _sb.auth.signUp({

    email: email, password: pw,

    options: { data: { full_name: name } }

  });

  if (res.error) {

    showMsg('su-msg', res.error.message, 'error');

    btn.disabled = false; btn.textContent = 'Create Account';

  } else if (res.data && res.data.session) {

    // Email confirmation is OFF -- user is immediately signed in

    showMsg('su-msg','Account created! Signing you in...','success');

    setTimeout(function() { window.location.href = _nextUrl; }, 800);

  } else {

    // Email confirmation is ON -- user must confirm first

    showMsg('su-msg','Account created! \u2709\ufe0f Check your email and click the confirmation link, then sign in.','success');

    btn.disabled = false; btn.textContent = 'Create Account';

    setTimeout(function() { switchTab('signin'); }, 3000);

  }

}

async function handleGoogle() {

  if (!_sb) { alert('Add your Supabase anon key to .env to enable Google OAuth.'); return; }

  var res = await _sb.auth.signInWithOAuth({

    provider: 'google',

    options: { redirectTo: window.location.origin + _nextUrl }

  });

  if (res.error) showMsg('si-msg', res.error.message, 'error');

}

document.addEventListener('keydown', function(e) {

  if (e.key !== 'Enter') return;

  var signinVisible = document.getElementById('form-signin').style.display !== 'none';

  if (signinVisible) handleSignIn(); else handleSignUp();

});

</script>

</body>

</html>

"""

    return head + style + body + script

#                                                                            

# WORKSPACE PAGE

#                                                                            

_MCQ_TEMPLATES = [

    ("What is the primary purpose of {t}?",

     ["Performance only","Readability only","Core functionality","None of the above"],2),

    ("Which is a best practice in {t}?",

     ["Avoid abstractions","Write tests first","Skip docs","Hardcode values"],1),

    ("When should you prefer {t}?",

     ["Never","Always","When it clearly fits","Only in production"],2),

    ("What does {t} help you avoid?",

     ["Writing code","Repeated bugs and anti-patterns","Using libraries","Refactoring"],1),

    ("Which concept is closely related to {t}?",

     ["Random numbers","Abstraction and encapsulation","CSS styling","Database indexing"],1),

    ("How does {t} improve maintainability?",

     ["It does not","By hiding all code","By enforcing clear structure","By removing tests"],2),

    ("What advice helps a junior dev struggling with {t}?",

     ["Skip it","Start with small examples","Read the whole spec first","Use a different language"],1),

    ("What is a common mistake when first learning {t}?",

     ["Testing too much","Over-engineering before understanding basics","Writing comments","Using version control"],1),

    ("Which tool most commonly pairs with {t} in production?",

     ["Notepad","A linter CI pipeline or framework","MS Paint","Excel"],1),

    ("What is the best way to measure mastery of {t}?",

     ["Memorising docs","Building a project and reviewing it","Watching videos only","Asking others"],1),

    ("In {t}, what does edge case mean?",

     ["A CSS property","Input that tests boundary conditions","A runtime error","A design pattern"],1),

    ("Which of these is NOT a goal of {t}?",

     ["Clarity","Reusability","Obfuscation","Correctness"],2),

    ("How should you handle errors in {t}?",

     ["Ignore them","Catch log and recover gracefully","Always crash","Hide them"],1),

    ("What does refactoring mean in {t}?",

     ["Rewriting from scratch","Improving structure without changing behaviour","Deleting code","Adding features"],1),

    ("Which describes a well-tested {t} module?",

     ["No tests needed","Has unit and integration tests","Manual tests only","Tested once on release"],1),

    ("Why is documentation important in {t}?",

     ["It is not","It helps others understand intent","Only for managers","Slows development"],1),

    ("What is separation of concerns in {t}?",

     ["Mixing all logic","Splitting code into focused independent units","A security feature","A database term"],1),

    ("Which runtime characteristic matters most for {t} at scale?",

     ["Font size","Memory and CPU efficiency","Line count","File name"],1),

    ("What does DRY stand for in {t}?",

     ["Do Repeat Yourself","Dont Repeat Yourself","Dynamic Runtime Yield","Default Run Yesterday"],1),

    ("What is the role of abstraction in {t}?",

     ["Makes code slower","Hides complexity behind a clean interface","Removes all variables","Only used in OOP"],1),

    ("Which lifecycle stage benefits most from {t} knowledge?",

     ["Deployment only","Design implementation and review equally","Testing only","Monitoring only"],1),

    ("What is a code smell in {t}?",

     ["A syntax error","A sign of deeper design problems","A comment","A library"],1),

    ("How does version control relate to {t}?",

     ["It does not","It tracks changes and enables collaboration","It runs code","It replaces testing"],1),

    ("What is mocking used for in {t} tests?",

     ["Styling","Replacing real dependencies with controlled fakes","Deployment","Logging"],1),

    ("Which naming style improves {t} readability?",

     ["Single letters","Descriptive consistent names","Random words","Numbers only"],1),

    ("What is technical debt in a {t} codebase?",

     ["Money owed","Shortcuts that cost more effort later","A design pattern","A testing tool"],1),

    ("When should you optimise {t} code?",

     ["Always first","After profiling proves a bottleneck","Never","Before writing tests"],1),

    ("Which principle says a function should do one thing?",

     ["DRY","YAGNI","Single Responsibility Principle","Open-Closed Principle"],2),

    ("What does idempotent mean for a {t} operation?",

     ["Fast","Running it multiple times gives the same result","Random output","Only runs once"],1),

    ("How do you choose between two {t} approaches?",

     ["Pick the longer one","Benchmark and consider readability and maintenance","Flip a coin","Always pick the newer one"],1),

    ("What does SOLID stand for in {t} design?",

     ["A rock-hard codebase","Five OOP design principles","A testing framework","A deployment tool"],1),

    ("Why use interfaces or protocols in {t}?",

     ["To slow things down","To define contracts that decouple implementations","To add syntax","No reason"],1),

    ("What is a race condition risk in {t}?",

     ["CPU speed","Concurrent access causing inconsistent state","Memory leak","Infinite loop"],1),

    ("What does fail fast mean in {t}?",

     ["Deploy quickly","Detect and raise errors early","Skip tests","Use faster hardware"],1),

    ("Which pattern is most useful for {t} event handling?",

     ["Singleton","Observer Pub-Sub","Factory","Proxy"],1),

    ("What is the benefit of immutability in {t}?",

     ["Uses more RAM","Eliminates accidental state mutation bugs","Slows execution","Requires more files"],1),

    ("How does caching help {t} performance?",

     ["It does not","Stores computed results to avoid repeat work","Deletes old data","Adds latency"],1),

    ("What is a NullPointerException risk in {t}?",

     ["A CSS bug","Dereferencing an uninitialised or absent value","A missing import","A syntax error"],1),

    ("What is the purpose of a linter in {t}?",

     ["Run tests","Automatically flag style and potential errors","Deploy code","Compress files"],1),

    ("Which testing level tests a {t} module in isolation?",

     ["End-to-end","Unit testing","Load testing","Smoke testing"],1),

    ("What does loose coupling mean in {t}?",

     ["Buggy connections","Components depend minimally on each other","Tight integration","No dependencies"],1),

    ("What is a design pattern in {t}?",

     ["A colour scheme","A reusable solution to a common design problem","A bug fix","A deployment step"],1),

    ("When is recursion best for {t}?",

     ["Always","When the problem naturally divides into sub-problems","Never","Only for sorting"],1),

    ("What does O(n log n) tell you about a {t} algorithm?",

     ["It crashes on large input","Its runtime grows slightly faster than linear","It is always fast","It uses no memory"],1),

    ("How do you prevent SQL injection in a {t} application?",

     ["Disable the database","Use parameterised queries","Escape nothing","Store SQL in cookies"],1),

    ("What is a memory leak in {t}?",

     ["A fast program","Memory allocated but never released","A syntax error","A missing import"],1),

    ("What does CI/CD mean for {t} projects?",

     ["Code Issues Deployment","Continuous Integration Continuous Deployment","Central Index Cache Delete","Custom IDE Debug"],1),

    ("What is the difference between sync and async {t} code?",

     ["No difference","Async does not block while waiting for IO","Sync is always faster","Async only works in browsers"],1),

    ("Which data structure gives O(1) lookups in {t}?",

     ["Array","Hash map dictionary","Linked list","Stack"],1),

    ("What is the final step before merging a {t} pull request?",

     ["Delete the branch","Code review and passing all CI checks","Deploy to production","Write release notes"],1),

]

def _build_workspace_html(topic: str) -> str:

    # Load the clean HTML template  --  no string-concatenated JS

    import pathlib

    _tmpl_path = pathlib.Path(__file__).parent / "workspace_template.html"

    template = _tmpl_path.read_text(encoding="utf-8")

    topic_js = json.dumps(topic)

    roadmap_html = "".join(

        '<div class="road-step"><span class="step-num">' + str(i+1) + "</span>"

        "<div><strong>" + s + "</strong>"

        "<p>Understand the fundamentals and practise with real examples.</p></div></div>"

        for i, s in enumerate([

            "Introduction to " + topic,

            "Core concepts of " + topic,

            "Advanced " + topic + " patterns",

            "Common pitfalls in " + topic,

            "Real-world " + topic + " projects",

        ])

    )

    mcq_rows = []

    for tmpl_q, tmpl_opts, ans in _MCQ_TEMPLATES:

        q    = tmpl_q.replace("{t}", topic)

        opts = [o.replace("{t}", topic) for o in tmpl_opts]

        mcq_rows.append(json.dumps({"q": q, "opts": opts, "ans": ans}))

    mcq_bank_js = "[" + ",".join(mcq_rows) + "]"

    followups_js = json.dumps([

        "Great! Walk me through a real example of " + topic + ".",

        "How would you handle edge cases in " + topic + "?",

        "What are the performance implications of " + topic + " at scale?",

        "Compare " + topic + " to any alternatives you know.",

        "What is the most important thing about " + topic + " for a junior dev?",

    ])

    topic_safe = topic.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    page = (template

        .replace("{{TOPIC}}", topic_safe)

        .replace("{{SUPA_URL}}", SUPABASE_URL.replace('"', '\\"'))

        .replace("{{SUPA_ANON}}", SUPABASE_ANON.replace('"', '\\"'))

        .replace("{{ROADMAP_HTML}}", roadmap_html)

        .replace("{{MCQ_BANK_JSON}}", mcq_bank_js)

        .replace("{{FOLLOWUPS_JSON}}", followups_js)

    )

    return page

# ===========================================================================

# WORKSPACE CSS

# ===========================================================================

_WS_CSS = """*{box-sizing:border-box;margin:0;padding:0}

body{background:var(--ink);color:var(--text);font-family:'Inter',sans-serif;display:flex;flex-direction:column;min-height:100vh}

h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif;letter-spacing:-.02em}

:root{--ink:#0B0D10;--surface:#14171C;--surface-2:#1B1F26;--line:#262B33;--ember:#FF8A3D;--ember-dim:#7A4420;--steel:#7C8CA6;--text:#F1F2F4;--muted:#9298A6;--green:#4CAF50;--red:#ef5350}

.topbar{background:rgba(11,13,16,.9);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:56px;position:sticky;top:0;z-index:50}

.brand{display:flex;align-items:center;gap:8px;font-weight:600;font-size:15px}

.back-btn{font-size:13px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:6px 14px;border-radius:6px;transition:color .15s,border-color .15s}

.back-btn:hover{color:var(--text);border-color:var(--steel)}

.tabs{display:flex;gap:4px;padding:10px 24px;background:var(--surface-2);border-bottom:1px solid var(--line);overflow-x:auto;flex-shrink:0}

.tab{font-size:13px;padding:7px 16px;border-radius:6px;cursor:pointer;color:var(--muted);border:1px solid transparent;white-space:nowrap;transition:all .15s}

.tab:hover{color:var(--text)}.tab.active{background:var(--ink);color:var(--ember);border-color:var(--ember-dim)}

.content{flex:1;padding:32px 24px;max-width:960px;margin:0 auto;width:100%}

.panel{display:none}.panel.active{display:block}

.badge{display:inline-block;font-size:11px;padding:3px 8px;border-radius:4px;background:rgba(255,138,61,.12);color:var(--ember);border:1px solid var(--ember-dim);margin-bottom:16px}

.road-step{display:flex;gap:16px;padding:20px 0;border-bottom:1px solid var(--line)}

.road-step:last-child{border-bottom:none}

.step-num{width:32px;height:32px;border-radius:50%;background:var(--ember);color:#1A0E05;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0}

.road-step strong{font-size:16px;display:block;margin-bottom:4px}.road-step p{font-size:14px;color:var(--muted)}

.theory-section{margin-bottom:28px}.theory-section h3{font-size:18px;margin-bottom:10px;color:var(--ember)}

.theory-section p{font-size:15px;color:var(--muted);line-height:1.7}

.mistake-list{list-style:none;margin-top:16px}

.mistake-list li{padding:10px 0;border-bottom:1px solid var(--line);font-size:14px;color:var(--muted)}

.mistake-list li::before{content:"! ";color:var(--ember)}

.code-area{display:grid;grid-template-columns:1fr 1fr;gap:16px}

@media(max-width:700px){.code-area{grid-template-columns:1fr}}

.editor-box{background:var(--surface);border:1px solid var(--line);border-radius:10px;overflow:hidden}

.editor-header{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid var(--line);font-size:13px;color:var(--muted)}

.lang-select{background:var(--surface-2);border:1px solid var(--line);border-radius:6px;color:var(--text);padding:4px 8px;font-size:12px;cursor:pointer}

textarea.code-editor{width:100%;background:transparent;border:none;outline:none;color:#9AD1B0;font-family:'JetBrains Mono',monospace;font-size:13px;padding:16px;resize:none;min-height:260px;line-height:1.7}

.output-box{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px;font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--steel);min-height:310px;white-space:pre-wrap}

.run-btn{background:var(--ember);color:#1A0E05;border:none;border-radius:6px;padding:8px 18px;font-weight:600;font-size:13px;cursor:pointer;margin-top:10px}

.run-btn:hover{background:#ffa15e}

.mcq-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:12px}

.mcq-meta{font-size:13px;color:var(--muted)}.mcq-meta strong{color:var(--text)}

.progress-wrap{width:100%;background:var(--surface-2);border-radius:6px;height:8px;margin-bottom:20px}

.progress-bar{height:8px;border-radius:6px;background:var(--ember);transition:width .4s ease}

.mcq-card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:24px;max-width:720px;animation:fadeUp .3s ease}

@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}

.q-number{font-size:12px;color:var(--ember);font-weight:600;margin-bottom:8px}

.q-text{font-size:16px;font-weight:500;margin-bottom:20px;line-height:1.5}

.opts{display:flex;flex-direction:column;gap:10px}

.opt{display:flex;align-items:center;gap:12px;font-size:14px;padding:12px 16px;border-radius:8px;border:1px solid var(--line);cursor:pointer;transition:border-color .15s,background .15s;user-select:none}

.opt:hover:not(.locked){border-color:var(--ember-dim);background:rgba(255,138,61,.06)}

.opt.correct{border-color:var(--green);background:rgba(76,175,80,.1);color:var(--green)}

.opt.wrong{border-color:var(--red);background:rgba(239,83,80,.1);color:var(--red)}

.opt.locked{pointer-events:none}

.opt-letter{width:26px;height:26px;border-radius:50%;background:var(--surface-2);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0}

.opt.correct .opt-letter{background:var(--green);border-color:var(--green);color:#fff}

.opt.wrong .opt-letter{background:var(--red);border-color:var(--red);color:#fff}

.mcq-feedback{margin-top:14px;font-size:13px;color:var(--muted);padding:12px 14px;background:var(--surface-2);border-radius:8px;display:none}

.mcq-feedback.show{display:block}

.mcq-nav{display:flex;align-items:center;justify-content:space-between;margin-top:20px;flex-wrap:wrap;gap:10px}

.mcq-stat{font-size:13px;color:var(--muted)}.mcq-stat .correct-c{color:var(--green);font-weight:600}.mcq-stat .wrong-c{color:var(--red);font-weight:600}

.score-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:200;align-items:center;justify-content:center}

.score-overlay.show{display:flex}

.score-modal{background:var(--surface);border:1px solid var(--ember-dim);border-radius:16px;padding:40px;max-width:480px;width:90%;text-align:center;animation:fadeUp .4s ease}

.score-modal h2{font-size:28px;margin-bottom:8px}

.score-circle{width:120px;height:120px;border-radius:50%;border:4px solid var(--ember);display:flex;align-items:center;justify-content:center;margin:24px auto;font-family:'Space Grotesk',sans-serif;font-size:32px;font-weight:700}

.score-breakdown{display:flex;justify-content:center;gap:32px;margin:20px 0;font-size:14px}

.score-breakdown .sb-correct{color:var(--green)}.score-breakdown .sb-wrong{color:var(--red)}

.score-modal p{color:var(--muted);font-size:14px;margin-bottom:24px}

.score-modal-btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}

.interview-wrap{display:grid;grid-template-columns:1.1fr .9fr;gap:24px;align-items:start}

@media(max-width:800px){.interview-wrap{grid-template-columns:1fr}}

.interview-box{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:24px}

.chat-log{min-height:200px;max-height:340px;overflow-y:auto;margin-bottom:16px;display:flex;flex-direction:column;gap:12px}

.msg{padding:12px 16px;border-radius:8px;font-size:14px;line-height:1.6;max-width:90%}

.msg.ai{background:var(--surface-2);border:1px solid var(--line);align-self:flex-start}

.msg.user{background:rgba(255,138,61,.1);border:1px solid var(--ember-dim);align-self:flex-end}

.answer-input{width:100%;background:var(--surface-2);border:1px solid var(--line);border-radius:8px;color:var(--text);font-family:'Inter',sans-serif;font-size:14px;padding:12px 14px;outline:none;resize:none;min-height:72px}

.answer-input:focus{border-color:var(--ember-dim)}

.interview-btns{display:flex;gap:10px;margin-top:10px;flex-wrap:wrap}

.btn-ghost{background:transparent;border:1px solid var(--line);color:var(--text);border-radius:6px;padding:8px 16px;font-size:13px;cursor:pointer}

.btn-ghost:hover{border-color:var(--steel)}

.mic-btn{display:flex;align-items:center;gap:6px;background:var(--surface-2);border:1px solid var(--line);color:var(--text);border-radius:6px;padding:8px 16px;font-size:13px;cursor:pointer;transition:all .2s}

.mic-btn.recording{background:rgba(239,83,80,.15);border-color:var(--red);color:var(--red);animation:pulse 1s infinite}

@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(239,83,80,.4)}50%{box-shadow:0 0 0 6px rgba(239,83,80,0)}}

.voice-status{font-size:12px;color:var(--muted);margin-top:8px;min-height:18px}

.tts-indicator{font-size:12px;color:var(--ember);margin-top:4px;display:none}.tts-indicator.speaking{display:block}

.i-score-card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:20px}

.i-score-card h3{font-size:16px;margin-bottom:16px;color:var(--ember)}

.score-row{display:flex;align-items:center;gap:12px;margin-bottom:12px}

.score-label{font-size:13px;color:var(--muted);width:120px;flex-shrink:0}

.score-bar-wrap{flex:1;background:var(--surface-2);border-radius:4px;height:6px}

.score-bar{height:6px;border-radius:4px;background:var(--ember);width:0;transition:width 1s ease}

.score-val{font-size:13px;font-weight:600;width:32px;text-align:right}

.video-tabs{display:flex;gap:8px;margin-bottom:20px}

.vtab{font-size:13px;padding:6px 16px;border-radius:6px;cursor:pointer;color:var(--muted);border:1px solid var(--line);transition:all .15s}

.vtab.active{background:var(--ink);color:var(--ember);border-color:var(--ember-dim)}

.video-player-wrap{width:100%;max-width:780px;aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:#000;border:1px solid var(--line);margin-bottom:20px}

.video-player-wrap iframe{width:100%;height:100%;border:none}

.video-list{display:flex;flex-direction:column;gap:10px;max-width:780px}

.vcard{display:flex;gap:12px;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 16px;cursor:pointer;transition:border-color .15s}

.vcard:hover,.vcard.active{border-color:var(--ember-dim)}.vcard.active{background:rgba(255,138,61,.06)}

.vcard-thumb{width:40px;height:40px;border-radius:8px;background:#c00;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}

.vcard-title{font-size:14px;font-weight:500;margin-bottom:3px;color:var(--text)}.vcard-ch{font-size:12px;color:var(--muted)}

.vload-msg{font-size:14px;color:var(--muted);padding:20px 0;text-align:center}

.cheat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}

.cheat-item{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:16px}

.cheat-item .lbl{font-size:12px;color:var(--ember);font-weight:600;margin-bottom:6px}

.cheat-item .detail{font-size:13px;color:var(--muted);font-family:'JetBrains Mono',monospace;line-height:1.6}"""

