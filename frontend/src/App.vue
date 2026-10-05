<script setup>
import { computed, onMounted, ref } from 'vue'

const api = '/api'
const active = ref('dashboard')
const summary = ref({income:0,expenses:0,balance:0,recentTransactions:[],categories:[],openTasks:0,plannedStudyMinutes:0})
const transactions = ref([])
const tasks = ref([])
const study = ref([])
const error = ref('')
const saving = ref(false)
const form = ref({type:'expense',amount:'',category:'Food',note:''})
const taskName = ref('')
const taskPriority = ref('medium')
const studyForm = ref({subject:'',duration:60,date:new Date().toISOString().slice(0,10)})

const money = n => new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR'}).format(Number(n||0))
const spendingMax = computed(()=>Math.max(...summary.value.categories.map(x=>Number(x.total)),1))

async function request(url, options={}) {
  const res = await fetch(api + url, {headers:{'Content-Type':'application/json',...(options.headers||{})},...options})
  if (!res.ok) throw new Error((await res.json().catch(()=>({}))).error || 'Request failed')
  return res.json()
}
async function load() {
  error.value=''
  try {
    summary.value=await request('/summary')
    transactions.value=await request('/transactions')
    tasks.value=await request('/tasks')
    study.value=await request('/study')
  } catch(e) { error.value=e.message }
}
async function runAction(action) {
  error.value=''
  saving.value=true
  try { await action(); await load() } catch(e) { error.value=e.message } finally { saving.value=false }
}
function addTransaction() {
  if (!form.value.amount) { error.value='Enter an amount before adding the transaction.'; return }
  runAction(async()=>{ await request('/transactions',{method:'POST',body:JSON.stringify(form.value)}); form.value={type:'expense',amount:'',category:'Food',note:''} })
}
function removeTransaction(id){ runAction(()=>request('/transactions/'+id,{method:'DELETE'})) }
function addTask() {
  if (!taskName.value.trim()) { error.value='Enter a task before adding it.'; return }
  runAction(async()=>{ await request('/tasks',{method:'POST',body:JSON.stringify({name:taskName.value,priority:taskPriority.value})}); taskName.value='' })
}
function toggleTask(id){ runAction(()=>request('/tasks/'+id,{method:'PATCH'})) }
function removeTask(id){ runAction(()=>request('/tasks/'+id,{method:'DELETE'})) }
function addStudy() {
  if (!studyForm.value.subject.trim()) { error.value='Enter a subject before adding the study session.'; return }
  runAction(async()=>{ await request('/study',{method:'POST',body:JSON.stringify(studyForm.value)}); studyForm.value={subject:'',duration:60,date:new Date().toISOString().slice(0,10)} })
}
function toggleStudy(id){ runAction(()=>request('/study/'+id,{method:'PATCH'})) }
onMounted(load)
</script>

<template>
  <div class="landscape" aria-hidden="true">
    <div class="sun-glow"></div><div class="sun"></div>
    <div class="cloud cloud-one"></div><div class="cloud cloud-two"></div>
    <div class="mountain mountain-back"></div><div class="mountain mountain-front"></div>
    <div class="field-glow"></div><div class="grass-line grass-line-one"></div><div class="grass-line grass-line-two"></div>
    <div class="fireflies"><i v-for="n in 18" :key="n" :style="{'--i':n}"></i></div>
  </div>

  <div class="app-shell">
    <aside class="sidebar glass-card">
      <div class="brand"><div class="brand-mark">✦</div><div><b>PRODUCTIVITY</b><small>SUITE</small></div></div>
      <div class="weather-note"><span class="weather-dot"></span><div><strong>SUNSET MODE</strong><small>Slow down. Make progress.</small></div></div>
      <nav>
        <button v-for="item in [['dashboard','Overview','⌂'],['transactions','Budget','◇'],['tasks','Tasks','✓'],['study','Study Planner','✎']]" :key="item[0]" :class="{active:active===item[0]}" @click="active=item[0]"><span>{{item[2]}}</span>{{item[1]}}</button>
      </nav>
      <div class="side-note"><span>TAKE IT ONE</span><strong>DAY AT A TIME.</strong></div>
    </aside>

    <main>
      <header>
        <div>
          <span class="eyebrow">PERSONAL PRODUCTIVITY SYSTEM</span>
          <h1>{{active==='dashboard'?'A little progress goes a long way.':active==='transactions'?'Your money, clearly.':active==='tasks'?'Keep your next steps visible.':'Give your goals some quiet time.'}}</h1>
          <p class="intro">{{active==='dashboard'?'A calm place to keep track of what matters.':active==='transactions'?'Record income and expenses without losing the bigger picture.':active==='tasks'?'Capture the work, choose a priority, then move it forward.':'Plan focused sessions and build a rhythm you can keep.'}}</p>
        </div>
        <div class="date-card"><span>LOCAL DATE</span><strong>{{new Date().toLocaleDateString('en-ZA',{weekday:'long',day:'numeric',month:'long'})}}</strong></div>
      </header>

      <div v-if="error" class="error glass-card" role="alert"><span>{{error}}</span><button @click="load">TRY AGAIN</button></div>

      <section v-if="active==='dashboard'" class="page">
        <div class="stats">
          <article class="stat-card glass-card"><span>BALANCE</span><strong>{{money(summary.balance)}}</strong><small>Income minus expenses</small></article>
          <article class="stat-card glass-card"><span>INCOME</span><strong>{{money(summary.income)}}</strong><small>Total recorded</small></article>
          <article class="stat-card glass-card"><span>EXPENSES</span><strong>{{money(summary.expenses)}}</strong><small>Total recorded</small></article>
          <article class="stat-card glass-card"><span>OPEN TASKS</span><strong>{{summary.openTasks}}</strong><small>{{summary.plannedStudyMinutes}} study minutes planned</small></article>
        </div>
        <div class="grid-two">
          <article class="panel glass-card"><div class="panel-head"><div><span class="panel-kicker">MONEY FLOW</span><h2>Spending by category</h2></div><button @click="active='transactions'">OPEN BUDGET →</button></div><div v-if="!summary.categories.length" class="empty">No expenses yet. Enjoy the blank slate.</div><div v-for="c in summary.categories" :key="c.category" class="bar-row"><span>{{c.category}}</span><div><i :style="{width:(Number(c.total)/spendingMax*100)+'%'}"></i></div><b>{{money(c.total)}}</b></div></article>
          <article class="panel glass-card"><div class="panel-head"><div><span class="panel-kicker">LATEST NOTES</span><h2>Recent transactions</h2></div><button @click="active='transactions'">SEE ALL →</button></div><div v-for="t in summary.recentTransactions" :key="t.id" class="list-row"><span><b>{{t.category}}</b><small>{{t.note||'No note'}}</small></span><strong :class="t.type">{{t.type==='expense'?'-':'+'}}{{money(t.amount)}}</strong></div><div v-if="!summary.recentTransactions.length" class="empty">Add your first transaction.</div></article>
        </div>
        <article class="quote-card glass-card"><span>FIELD NOTE</span><p>“You do not have to finish everything today. You only have to keep moving.”</p></article>
      </section>

      <section v-if="active==='transactions'" class="page">
        <article class="panel glass-card form-panel"><div><span class="panel-kicker">MONEY FLOW</span><h2>Add transaction</h2></div><div class="form-grid"><select v-model="form.type"><option value="expense">Expense</option><option value="income">Income</option></select><input v-model="form.amount" type="number" min="0" step="0.01" placeholder="Amount (R)"><input v-model="form.category" placeholder="Category"><input v-model="form.note" placeholder="Note"><button :disabled="saving" @click="addTransaction">{{saving?'SAVING…':'ADD TRANSACTION'}}</button></div></article>
        <article class="panel glass-card"><div class="panel-head"><div><span class="panel-kicker">YOUR RECORD</span><h2>Transaction history</h2></div><span class="record-count">{{transactions.length}} records</span></div><div v-for="t in transactions" :key="t.id" class="list-row"><span><b>{{t.category}}</b><small>{{t.note||'No note'}} · {{t.date}}</small></span><span class="row-action"><strong :class="t.type">{{t.type==='expense'?'-':'+'}}{{money(t.amount)}}</strong><button class="delete" @click="removeTransaction(t.id)">×</button></span></div><div v-if="!transactions.length" class="empty">No transactions yet.</div></article>
      </section>

      <section v-if="active==='tasks'" class="page">
        <article class="panel glass-card form-panel"><div><span class="panel-kicker">NEXT STEPS</span><h2>New task</h2></div><div class="form-grid"><input v-model="taskName" @keyup.enter="addTask" placeholder="What needs doing?"><select v-model="taskPriority"><option>low</option><option>medium</option><option>high</option></select><button :disabled="saving" @click="addTask">{{saving?'SAVING…':'ADD TASK'}}</button></div></article>
        <article class="panel glass-card"><div v-for="t in tasks" :key="t.id" class="task-row" :class="{done:t.done}"><label class="check-wrap"><input type="checkbox" :checked="t.done" @change="toggleTask(t.id)"><span class="check"></span></label><span class="task-copy"><b>{{t.name}}</b><small>{{t.priority}} priority</small></span><button class="delete" @click="removeTask(t.id)">×</button></div><div v-if="!tasks.length" class="empty">Nothing here yet. Add one small thing.</div></article>
      </section>

      <section v-if="active==='study'" class="page">
        <article class="panel glass-card form-panel"><div><span class="panel-kicker">QUIET WORK</span><h2>Plan a study session</h2></div><div class="form-grid"><input v-model="studyForm.subject" placeholder="Subject / topic"><input v-model="studyForm.duration" type="number" min="1" max="480" placeholder="Minutes"><input v-model="studyForm.date" type="date"><button :disabled="saving" @click="addStudy">{{saving?'SAVING…':'ADD SESSION'}}</button></div></article>
        <article class="panel glass-card"><div v-for="s in study" :key="s.id" class="task-row" :class="{done:s.done}"><label class="check-wrap"><input type="checkbox" :checked="s.done" @change="toggleStudy(s.id)"><span class="check"></span></label><span class="task-copy"><b>{{s.subject}}</b><small>{{s.duration}} minutes · {{s.date}}</small></span></div><div v-if="!study.length" class="empty">Plan your first session and make some space for yourself.</div></article>
      </section>
    </main>
  </div>
</template>
