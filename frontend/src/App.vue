 <script setup>
import { computed, onMounted, ref } from 'vue'

const api = '/api'
const active = ref('dashboard')
const summary = ref({income:0,expenses:0,balance:0,recentTransactions:[],categories:[],openTasks:0,plannedStudyMinutes:0})
const transactions = ref([])
const tasks = ref([])
const study = ref([])
const error = ref('')
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
async function addTransaction(){ if(!form.value.amount)return; await request('/transactions',{method:'POST',body:JSON.stringify(form.value)}); form.value={type:'expense',amount:'',category:'Food',note:''}; await load() }
async function removeTransaction(id){await request('/transactions/'+id,{method:'DELETE'});await load()}
async function addTask(){if(!taskName.value)return;await request('/tasks',{method:'POST',body:JSON.stringify({name:taskName.value,priority:taskPriority.value})});taskName.value='';await load()}
async function toggleTask(id){await request('/tasks/'+id,{method:'PATCH'});await load()}
async function removeTask(id){await request('/tasks/'+id,{method:'DELETE'});await load()}
async function addStudy(){if(!studyForm.value.subject)return;await request('/study',{method:'POST',body:JSON.stringify(studyForm.value)});studyForm.value={subject:'',duration:60,date:new Date().toISOString().slice(0,10)};await load()}
async function toggleStudy(id){await request('/study/'+id,{method:'PATCH'});await load()}
onMounted(load)
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand"><span class="brand-mark">P</span><div><b>PRODUCTIVITY</b><small>SUITE</small></div></div>
      <nav><button v-for="item in [['dashboard','Dashboard'],['transactions','Budget'],['tasks','Tasks'],['study','Study Planner']]" :key="item[0]" :class="{active:active===item[0]}" @click="active=item[0]">{{item[1]}}</button></nav>
      <div class="side-note">BUILD BETTER<br><strong>ONE DAY AT A TIME.</strong></div>
    </aside>

    <main>
      <header><div><span class="eyebrow">PERSONAL PRODUCTIVITY SYSTEM</span><h1>{{active==='dashboard'?'Good day. Let’s get organised.':active==='transactions'?'Budget tracker':active==='tasks'?'Task board':'Study planner'}}</h1></div><span class="date">{{new Date().toLocaleDateString('en-ZA',{weekday:'long',day:'numeric',month:'long'})}}</span></header>
      <div v-if="error" class="error">{{error}} <button @click="load">Retry</button></div>

      <section v-if="active==='dashboard'" class="page">
        <div class="stats">
          <article><span>BALANCE</span><strong>{{money(summary.balance)}}</strong><small>Income minus expenses</small></article>
          <article><span>INCOME</span><strong>{{money(summary.income)}}</strong><small>Total recorded</small></article>
          <article><span>EXPENSES</span><strong>{{money(summary.expenses)}}</strong><small>Total recorded</small></article>
          <article><span>OPEN TASKS</span><strong>{{summary.openTasks}}</strong><small>{{summary.plannedStudyMinutes}} study minutes planned</small></article>
        </div>
        <div class="grid-two">
          <article class="panel"><div class="panel-head"><h2>Spending by category</h2><button @click="active='transactions'">VIEW BUDGET →</button></div><div v-if="!summary.categories.length" class="empty">No expenses yet.</div><div v-for="c in summary.categories" :key="c.category" class="bar-row"><span>{{c.category}}</span><div><i :style="{width:(Number(c.total)/spendingMax*100)+'%'}"></i></div><b>{{money(c.total)}}</b></div></article>
          <article class="panel"><div class="panel-head"><h2>Recent transactions</h2><button @click="active='transactions'">SEE ALL →</button></div><div v-for="t in summary.recentTransactions" :key="t.id" class="list-row"><span><b>{{t.category}}</b><small>{{t.note||'No note'}}</small></span><strong :class="t.type">{{t.type==='expense'?'-':'+'}}{{money(t.amount)}}</strong></div><div v-if="!summary.recentTransactions.length" class="empty">Add your first transaction.</div></article>
        </div>
      </section>

      <section v-if="active==='transactions'" class="page">
        <article class="panel form-panel"><h2>Add transaction</h2><div class="form-grid"><select v-model="form.type"><option value="expense">Expense</option><option value="income">Income</option></select><input v-model="form.amount" type="number" min="0" placeholder="Amount (R)" /><input v-model="form.category" placeholder="Category" /><input v-model="form.note" placeholder="Note" /><button @click="addTransaction">ADD TRANSACTION</button></div></article>
        <article class="panel"><div class="panel-head"><h2>Transaction history</h2><span>{{transactions.length}} records</span></div><div v-for="t in transactions" :key="t.id" class="list-row"><span><b>{{t.category}}</b><small>{{t.note||'No note'}} · {{t.date}}</small></span><span><strong :class="t.type">{{t.type==='expense'?'-':'+'}}{{money(t.amount)}}</strong> <button class="delete" @click="removeTransaction(t.id)">×</button></span></div></article>
      </section>

      <section v-if="active==='tasks'" class="page">
        <article class="panel form-panel"><h2>New task</h2><div class="form-grid"><input v-model="taskName" @keyup.enter="addTask" placeholder="What needs doing?" /><select v-model="taskPriority"><option>low</option><option>medium</option><option>high</option></select><button @click="addTask">ADD TASK</button></div></article>
        <article class="panel"><div v-for="t in tasks" :key="t.id" class="task-row" :class="{done:t.done}"><input type="checkbox" :checked="t.done" @change="toggleTask(t.id)" /><span><b>{{t.name}}</b><small>{{t.priority}} priority</small></span><button class="delete" @click="removeTask(t.id)">×</button></div><div v-if="!tasks.length" class="empty">Nothing here yet. Add a task.</div></article>
      </section>

      <section v-if="active==='study'" class="page">
        <article class="panel form-panel"><h2>Plan a study session</h2><div class="form-grid"><input v-model="studyForm.subject" placeholder="Subject / topic" /><input v-model="studyForm.duration" type="number" min="1" max="480" placeholder="Minutes" /><input v-model="studyForm.date" type="date" /><button @click="addStudy">ADD SESSION</button></div></article>
        <article class="panel"><div v-for="s in study" :key="s.id" class="task-row" :class="{done:s.done}"><input type="checkbox" :checked="s.done" @change="toggleStudy(s.id)" /><span><b>{{s.subject}}</b><small>{{s.duration}} minutes · {{s.date}}</small></span></div><div v-if="!study.length" class="empty">Plan your first study session.</div></article>
      </section>
    </main>
  </div>
</template>
