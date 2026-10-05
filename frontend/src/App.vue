<script setup>
import { computed, onMounted, ref } from 'vue'

const api = '/api'

const active = ref('dashboard')
const summary = ref({
  income: 0,
  expenses: 0,
  balance: 0,
  recentTransactions: [],
  categories: [],
  openTasks: 0,
  plannedStudyMinutes: 0,
  startDate: '',
  endDate: ''
})
const transactions = ref([])
const tasks = ref([])
const study = ref([])
const budgets = ref([])
const selectedBudget = ref(null)
const settings = ref({
  resetFrequency: 'monthly',
  currentPeriod: null
})
const error = ref('')
const saving = ref(false)
const isNight = ref(localStorage.getItem('productivity-theme') === 'night')

const form = ref({
  type: 'expense',
  amount: '',
  category: 'Food',
  note: ''
})

const taskName = ref('')
const taskPriority = ref('medium')

const studyForm = ref({
  subject: '',
  duration: 60,
  date: localDateString()
})

function localDateString() {
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Africa/Johannesburg',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })

  return formatter.format(new Date())
}

const money = (n) => {
  return new Intl.NumberFormat('en-ZA', {
    style: 'currency',
    currency: 'ZAR'
  }).format(Number(n || 0))
}

const spendingMax = computed(() => {
  return Math.max(
    ...summary.value.categories.map((item) => Number(item.total)),
    1
  )
})

const frequencyLabel = computed(() => {
  const labels = {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    yearly: 'Yearly'
  }

  return labels[settings.value.resetFrequency] || 'Monthly'
})

const periodLabel = computed(() => {
  const start = summary.value.startDate
  const end = summary.value.endDate

  if (!start) {
    return 'Current budget'
  }

  return start === end ? start : `${start} → ${end}`
})

function toggleTheme() {
  isNight.value = !isNight.value
  localStorage.setItem(
    'productivity-theme',
    isNight.value ? 'night' : 'sunset'
  )
}

async function request(url, options = {}) {
  const response = await fetch(api + url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new Error(payload.error || 'Request failed')
  }

  return response.json()
}

async function loadAll() {
  error.value = ''

  try {
    const [
      summaryData,
      transactionData,
      taskData,
      studyData,
      settingsData,
      budgetData
    ] = await Promise.all([
      request('/summary'),
      request('/transactions'),
      request('/tasks'),
      request('/study'),
      request('/settings'),
      request('/budgets')
    ])

    summary.value = summaryData
    transactions.value = transactionData
    tasks.value = taskData
    study.value = studyData
    settings.value = settingsData
    budgets.value = budgetData
  } catch (err) {
    error.value = err.message
  }
}

async function loadBudget(id) {
  try {
    selectedBudget.value = await request('/budgets/' + id)
  } catch (err) {
    error.value = err.message
  }
}

async function runAction(action) {
  error.value = ''
  saving.value = true

  try {
    await action()
    await loadAll()
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

function addTransaction() {
  if (!form.value.amount) {
    error.value = 'Enter an amount before adding the transaction.'
    return
  }

  runAction(async () => {
    await request('/transactions', {
      method: 'POST',
      body: JSON.stringify(form.value)
    })

    form.value = {
      type: 'expense',
      amount: '',
      category: 'Food',
      note: ''
    }
  })
}

function removeTransaction(id) {
  runAction(() => {
    return request('/transactions/' + id, {
      method: 'DELETE'
    })
  })
}

function addTask() {
  if (!taskName.value.trim()) {
    error.value = 'Enter a task before adding it.'
    return
  }

  runAction(async () => {
    await request('/tasks', {
      method: 'POST',
      body: JSON.stringify({
        name: taskName.value,
        priority: taskPriority.value
      })
    })

    taskName.value = ''
  })
}

function toggleTask(id) {
  runAction(() => {
    return request('/tasks/' + id, {
      method: 'PATCH'
    })
  })
}

function removeTask(id) {
  runAction(() => {
    return request('/tasks/' + id, {
      method: 'DELETE'
    })
  })
}

function addStudy() {
  if (!studyForm.value.subject.trim()) {
    error.value = 'Enter a subject before adding the study session.'
    return
  }

  runAction(async () => {
    await request('/study', {
      method: 'POST',
      body: JSON.stringify(studyForm.value)
    })

    studyForm.value = {
      subject: '',
      duration: 60,
      date: localDateString()
    }
  })
}

function toggleStudy(id) {
  runAction(() => {
    return request('/study/' + id, {
      method: 'PATCH'
    })
  })
}

async function saveSettings() {
  await runAction(async () => {
    const updated = await request('/settings', {
      method: 'PATCH',
      body: JSON.stringify({
        resetFrequency: settings.value.resetFrequency
      })
    })

    settings.value = {
      ...settings.value,
      ...updated
    }

    selectedBudget.value = null
  })
}

function openHistory() {
  active.value = 'history'
}

async function viewBudget(id) {
  await loadBudget(id)
  active.value = 'history'
}

onMounted(loadAll)
</script>

<template>
  <div class="landscape" :class="{night:isNight}" aria-hidden="true">
    <div class="sun-glow"></div><div class="sun"></div><div class="moon-glow"></div><div class="moon"><span></span></div>
    <div class="cloud cloud-one"></div><div class="cloud cloud-two"></div>
    <div class="mountain mountain-back"></div><div class="mountain mountain-front"></div>
    <div class="field-glow"></div><div class="grass-line grass-line-one"></div><div class="grass-line grass-line-two"></div>
    <div class="fireflies"><i v-for="n in 18" :key="n" :style="{'--i':n}"></i></div>
  </div>

  <div class="app-shell" :class="{night:isNight}">
    <aside class="sidebar glass-card">
      <div class="brand"><div class="brand-mark">✦</div><div><b>PRODUCTIVITY</b><small>SUITE</small></div></div>
      <div class="weather-note"><span class="weather-dot"></span><div><strong>{{isNight?'MOONLIGHT MODE':'SUNSET MODE'}}</strong><small>{{isNight?'A quieter night for focused work.':'Slow down. Make progress.'}}</small></div></div>
      <nav>
        <button v-for="item in [['dashboard','Overview','⌂'],['transactions','Budget','◇'],['tasks','Tasks','✓'],['study','Study Planner','✎'],['history','Budget History','◷'],['settings','Settings','⚙']]" :key="item[0]" :class="{active:active===item[0]}" @click="active=item[0]"><span>{{item[2]}}</span>{{item[1]}}</button>
      </nav>
      <button class="theme-toggle" @click="toggleTheme"><span class="theme-icon">{{isNight?'☀':'☾'}}</span><span><b>{{isNight?'SUNSET':'MOONLIGHT'}}</b><small>{{isNight?'Return to golden hour':'Switch to night'}}</small></span></button>
      <div class="side-note"><span>TAKE IT ONE</span><strong>DAY AT A TIME.</strong></div>
    </aside>

    <main>
      <header>
        <div>
          <span class="eyebrow">PERSONAL PRODUCTIVITY SYSTEM</span>
          <h1>{{active==='dashboard'?'A little progress goes a long way.':active==='transactions'?'Your money, clearly.':active==='tasks'?'Keep your next steps visible.':active==='study'?'Give your goals some quiet time.':active==='history'?'Nothing gets lost.':'Make the system yours.'}}</h1>
          <p class="intro">{{active==='dashboard'?'A calm place to keep track of what matters.':active==='transactions'?'Record income and expenses without losing the bigger picture.':active==='tasks'?'Capture the work, choose a priority, then move it forward.':active==='study'?'Plan focused sessions and build a rhythm you can keep.':active==='history'?'Every completed budget stays here so you can look back, compare and learn.':'Choose how often your budget begins a fresh chapter. Your old chapters stay safe.'}}</p>
        </div>
        <div class="date-card"><span>{{frequencyLabel.toUpperCase()}} BUDGET</span><strong>{{periodLabel}}</strong></div>
      </header>

      <div v-if="error" class="error glass-card" role="alert"><span>{{error}}</span><button @click="loadAll">TRY AGAIN</button></div>

      <section v-if="active==='dashboard'" class="page">
        <div class="period-banner glass-card"><div><span class="panel-kicker">CURRENT {{frequencyLabel.toUpperCase()}} PERIOD</span><h2>{{periodLabel}}</h2><small>This period will close automatically when the next {{settings.resetFrequency}} begins.</small></div><button @click="openHistory">VIEW OLD BUDGETS →</button></div>
        <div class="stats">
          <article class="stat-card glass-card"><span>BALANCE</span><strong>{{money(summary.balance)}}</strong><small>Income minus expenses</small></article>
          <article class="stat-card glass-card"><span>INCOME</span><strong>{{money(summary.income)}}</strong><small>This {{settings.resetFrequency}} period</small></article>
          <article class="stat-card glass-card"><span>EXPENSES</span><strong>{{money(summary.expenses)}}</strong><small>This {{settings.resetFrequency}} period</small></article>
          <article class="stat-card glass-card"><span>OPEN TASKS</span><strong>{{summary.openTasks}}</strong><small>{{summary.plannedStudyMinutes}} study minutes planned</small></article>
        </div>
        <div class="grid-two">
          <article class="panel glass-card"><div class="panel-head"><div><span class="panel-kicker">MONEY FLOW</span><h2>Spending by category</h2></div><button @click="active='transactions'">OPEN BUDGET →</button></div><div v-if="!summary.categories.length" class="empty">No expenses in this period. Enjoy the blank slate.</div><div v-for="c in summary.categories" :key="c.category" class="bar-row"><span>{{c.category}}</span><div><i :style="{width:(Number(c.total)/spendingMax*100)+'%'}"></i></div><b>{{money(c.total)}}</b></div></article>
          <article class="panel glass-card"><div class="panel-head"><div><span class="panel-kicker">LATEST NOTES</span><h2>Recent transactions</h2></div><button @click="active='transactions'">SEE ALL →</button></div><div v-for="t in summary.recentTransactions" :key="t.id" class="list-row"><span><b>{{t.category}}</b><small>{{t.note||'No note'}}</small></span><strong :class="t.type">{{t.type==='expense'?'-':'+'}}{{money(t.amount)}}</strong></div><div v-if="!summary.recentTransactions.length" class="empty">Add your first transaction.</div></article>
        </div>
        <article class="quote-card glass-card"><span>FIELD NOTE</span><p>“You do not have to finish everything today. You only have to keep moving.”</p></article>
      </section>

      <section v-if="active==='transactions'" class="page">
        <article class="panel glass-card form-panel"><div><span class="panel-kicker">MONEY FLOW · {{frequencyLabel.toUpperCase()}}</span><h2>Add transaction</h2></div><div class="form-grid"><select v-model="form.type"><option value="expense">Expense</option><option value="income">Income</option></select><input v-model="form.amount" type="number" min="0" step="0.01" placeholder="Amount (R)"><input v-model="form.category" placeholder="Category"><input v-model="form.note" placeholder="Note"><button :disabled="saving" @click="addTransaction">{{saving?'SAVING…':'ADD TRANSACTION'}}</button></div></article>
        <article class="panel glass-card"><div class="panel-head"><div><span class="panel-kicker">CURRENT PERIOD · {{periodLabel}}</span><h2>Transaction history</h2></div><span class="record-count">{{transactions.length}} records</span></div><div v-for="t in transactions" :key="t.id" class="list-row"><span><b>{{t.category}}</b><small>{{t.note||'No note'}} · {{t.date}}</small></span><span class="row-action"><strong :class="t.type">{{t.type==='expense'?'-':'+'}}{{money(t.amount)}}</strong><button class="delete" @click="removeTransaction(t.id)">×</button></span></div><div v-if="!transactions.length" class="empty">No transactions in this period.</div></article>
      </section>

      <section v-if="active==='tasks'" class="page">
        <article class="panel glass-card form-panel"><div><span class="panel-kicker">NEXT STEPS</span><h2>New task</h2></div><div class="form-grid"><input v-model="taskName" @keyup.enter="addTask" placeholder="What needs doing?"><select v-model="taskPriority"><option>low</option><option>medium</option><option>high</option></select><button :disabled="saving" @click="addTask">{{saving?'SAVING…':'ADD TASK'}}</button></div></article>
        <article class="panel glass-card"><div v-for="t in tasks" :key="t.id" class="task-row" :class="{done:t.done}"><label class="check-wrap"><input type="checkbox" :checked="t.done" @change="toggleTask(t.id)"><span class="check"></span></label><span class="task-copy"><b>{{t.name}}</b><small>{{t.priority}} priority</small></span><button class="delete" @click="removeTask(t.id)">×</button></div><div v-if="!tasks.length" class="empty">Nothing here yet. Add one small thing.</div></article>
      </section>

      <section v-if="active==='study'" class="page">
        <article class="panel glass-card form-panel"><div><span class="panel-kicker">QUIET WORK</span><h2>Plan a study session</h2></div><div class="form-grid"><input v-model="studyForm.subject" placeholder="Subject / topic"><input v-model="studyForm.duration" type="number" min="1" max="480" placeholder="Minutes"><input v-model="studyForm.date" type="date"><button :disabled="saving" @click="addStudy">{{saving?'SAVING…':'ADD SESSION'}}</button></div></article>
        <article class="panel glass-card"><div v-for="s in study" :key="s.id" class="task-row" :class="{done:s.done}"><label class="check-wrap"><input type="checkbox" :checked="s.done" @change="toggleStudy(s.id)"><span class="check"></span></label><span class="task-copy"><b>{{s.subject}}</b><small>{{s.duration}} minutes · {{s.date}}</small></span></div><div v-if="!study.length" class="empty">Plan your first session and make some space for yourself.</div></article>
      </section>

      <section v-if="active==='history'" class="page">
        <article class="panel glass-card history-intro"><span class="panel-kicker">PERMANENT ARCHIVE</span><h2>Your old budgets stay here.</h2><p>When a period ends, its transactions and totals remain untouched. Pick any chapter below to inspect the full record.</p></article>
        <div class="history-grid">
          <article v-for="b in budgets" :key="b.id" class="history-card glass-card" :class="{current:b.isCurrent}">
            <div class="history-top"><span>{{b.isCurrent?'CURRENT':'ARCHIVED'}}</span><small>{{b.frequency}}</small></div>
            <h3>{{b.startDate}} <span>→</span> {{b.endDate}}</h3>
            <div class="history-money"><div><small>INCOME</small><strong>{{money(b.income)}}</strong></div><div><small>EXPENSES</small><strong>{{money(b.expenses)}}</strong></div><div><small>BALANCE</small><strong>{{money(b.balance)}}</strong></div></div>
            <div class="history-bottom"><small>{{b.transactionCount}} transactions</small><button @click="viewBudget(b.id)">VIEW BUDGET →</button></div>
          </article>
        </div>
        <article v-if="selectedBudget" class="panel glass-card selected-budget">
          <div class="panel-head"><div><span class="panel-kicker">ARCHIVE DETAIL</span><h2>{{selectedBudget.startDate}} → {{selectedBudget.endDate}}</h2></div><button @click="selectedBudget=null">CLOSE</button></div>
          <div class="stats compact"><article class="stat-card"><span>INCOME</span><strong>{{money(selectedBudget.income)}}</strong></article><article class="stat-card"><span>EXPENSES</span><strong>{{money(selectedBudget.expenses)}}</strong></article><article class="stat-card"><span>BALANCE</span><strong>{{money(selectedBudget.balance)}}</strong></article></div>
          <div v-for="t in selectedBudget.transactions" :key="t.id" class="list-row"><span><b>{{t.category}}</b><small>{{t.note||'No note'}} · {{t.date}}</small></span><strong :class="t.type">{{t.type==='expense'?'-':'+'}}{{money(t.amount)}}</strong></div>
        </article>
      </section>

      <section v-if="active==='settings'" class="page">
        <article class="panel glass-card settings-panel"><span class="panel-kicker">BUDGET CYCLE</span><h2>Choose when your budget resets.</h2><p>A reset starts a new budget period. <strong>Nothing is deleted.</strong> Your previous period is automatically archived and stays available in Budget History.</p>
        <div class="frequency-options">
          <label v-for="option in [['daily','Daily','New budget every day'],['weekly','Weekly','Monday → Sunday'],['monthly','Monthly','1st → last day'],['yearly','Yearly','January → December']]" :key="option[0]" :class="{selected:settings.resetFrequency===option[0]}"><input type="radio" v-model="settings.resetFrequency" :value="option[0]"><span class="freq-icon">{{option[0]==='daily'?'☀':option[0]==='weekly'?'◒':option[0]==='monthly'?'◔':'✦'}}</span><b>{{option[1]}}</b><small>{{option[2]}}</small></label>
        </div>
        <div class="settings-actions"><span>Current: <strong>{{frequencyLabel}}</strong></span><button :disabled="saving" @click="saveSettings">{{saving?'SAVING…':'SAVE BUDGET SETTINGS'}}</button></div></article>
        <article class="panel glass-card"><span class="panel-kicker">DATA GUARANTEE</span><h2>Your history is permanent.</h2><div class="guarantee-list"><div><b>✓ Transactions stay stored</b><small>Changing the reset frequency never removes old income or expenses.</small></div><div><b>✓ Old periods stay accessible</b><small>Every completed cycle appears in Budget History.</small></div><div><b>✓ New cycles start automatically</b><small>When you return after a boundary, the app creates the correct period for you.</small></div></div></article>
      </section>
    </main>
  </div>
</template>
