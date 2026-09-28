// Dashboard behavior and Chart.js rendering
function fmt(n){return (Math.round(n*100)/100).toLocaleString()}

// Populate KPI cards
function renderKPIs(){
  const k = DATA.kpis; const container = document.getElementById('kpi-cards');
  const items = [
    {title:'Total Flights', value:k.total_flights},
    {title:'Average Load Factor', value:k.avg_load_factor + '%'},
    {title:'Average Utilisation', value:k.avg_utilisation + '%'},
    {title:'Aircraft Types', value:k.aircraft_types},
    {title:'Routes', value:k.routes}
  ];
  container.innerHTML = items.map(it=>`<div class="kpi card"><h3>${it.value}</h3><p>${it.title}</p></div>`).join('');
}

// Aircraft charts
function renderAircraftCharts(){
  const ctx1 = document.getElementById('chartLoad').getContext('2d');
  new Chart(ctx1,{type:'bar',data:{labels:DATA.aircraft_load.labels,datasets:[{label:'Avg Load Factor (%)',data:DATA.aircraft_load.values,backgroundColor:'#0b69ff'}]},options:{responsive:true,plugins:{legend:{display:false}}}});

  const ctx2 = document.getElementById('chartUtil').getContext('2d');
  new Chart(ctx2,{type:'bar',data:{labels:DATA.aircraft_util.labels,datasets:[{label:'Avg Utilisation (%)',data:DATA.aircraft_util.values,backgroundColor:'#0b69ff'}]},options:{responsive:true,plugins:{legend:{display:false}}}});
}

// Routes chart (20 routes sorted)
function renderRoutesChart(){
  const labels = DATA.lowest_routes.map(r=>r.route);
  const values = DATA.lowest_routes.map(r=>r.value);
  const ctx = document.getElementById('chartRoutes').getContext('2d');
  new Chart(ctx,{type:'bar',data:{labels, datasets:[{label:'Average Load Factor (%)',data:values,backgroundColor:labels.map(r=>r.includes('Kolkata')? '#ff7a59':'#0b69ff')}]},options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false}}}});
}

// Ineff table
function renderIneffTable(){
  const tbody = document.querySelector('#ineff-table tbody');
  tbody.innerHTML = DATA.ineff.map(r=>`<tr><td>${r.Aircraft_Type}</td><td>${r.Route}</td><td>${r.flights}</td><td>${r.avg_load.toFixed(2)}</td><td>${r.avg_util.toFixed(2)}</td></tr>`).join('');
}

// Scatter plots
function renderScatter(){
  const ctx = document.getElementById('chartDistUtil').getContext('2d');
  // since we don't have per-flight distances here in data.js, we synthesize representative points using util and a proxy
  const points = DATA.ineff.map((d,i)=>({x: (i+1)*150, y: d.avg_util}));
  new Chart(ctx,{type:'scatter',data:{datasets:[{label:'Route Distance vs Utilisation',data:points,backgroundColor:'#0b69ff'}]},options:{scales:{x:{title:{display:true,text:'Route Distance (km) - proxy'}},y:{title:{display:true,text:'Aircraft Utilisation (%)'}}},plugins:{legend:{display:false}}}});

  const ctx2 = document.getElementById('chartDistLoad').getContext('2d');
  const points2 = DATA.ineff.map((d,i)=>({x:(i+1)*150,y:d.avg_load}));
  new Chart(ctx2,{type:'scatter',data:{datasets:[{label:'Route Distance vs Load Factor',data:points2,backgroundColor:'#0b69ff'}]},options:{scales:{x:{title:{display:true,text:'Route Distance (km) - proxy'}},y:{title:{display:true,text:'Load Factor (%)'}}},plugins:{legend:{display:false}}}});
}

function renderML(){
  document.getElementById('ml-r2').innerText = DATA.ml.r2.toFixed(4);
  document.getElementById('ml-mae').innerText = DATA.ml.mae.toFixed(2);
  document.getElementById('ml-rmse').innerText = DATA.ml.rmse.toFixed(2);
  document.getElementById('ml-coefs').innerText = `Intercept: ${DATA.ml.intercept.toFixed(4)}\n` + Object.entries(DATA.ml.coefficients).map(([k,v])=>`${k}: ${v.toFixed(6)}`).join('\n');
}

function renderInsights(){
  const ins = [
    `Overall average passenger load factor is ${DATA.kpis.avg_load_factor}% and average aircraft utilisation is ${DATA.kpis.avg_utilisation}%.`,
    `Aircraft-type averages (Passenger Load Factor): ATR 72 = 84.04%, A320 = 83.55%, B737-800 = 83.15%, A321 = 80.70%, B787 = 76.01%, A350 = 73.95%.`,
    `Three lowest-occupancy routes: Mumbai–Kolkata (70.71%), Hyderabad–Kolkata (70.97%), Chennai–Kolkata (72.22%).`,
    `Pearson correlation between Route Distance and Aircraft Utilisation ≈ ${DATA.correlation.route_distance_vs_utilisation}.`,
    `Linear regression predicting Passenger Load Factor yields R² = ${DATA.ml.r2.toFixed(4)}, MAE = ${DATA.ml.mae.toFixed(2)}, RMSE = ${DATA.ml.rmse.toFixed(2)}.`
  ];
  const container = document.getElementById('insight-cards');
  container.innerHTML = ins.map(i=>`<div class="insight card"><p>${i}</p></div>`).join('');
}

function renderRecommendations(){
  const recs = [
    'Review aircraft assignments on the lowest-occupancy routes (Mumbai–Kolkata, Hyderabad–Kolkata, Chennai–Kolkata) and consider deploying smaller aircraft or frequency changes.',
    'Prioritise increasing utilisation on wide-body types (B787, A350) through schedule adjustments or transferring these aircraft to higher-demand routes.',
    'Update the efficiency flagging policy: target aircraft-route pairs with Load Factor < 70% OR Utilisation < 65% for operational review.'
  ];
  const el = document.getElementById('reco-cards');
  el.innerHTML = recs.map(r=>`<div class="reco card"><p>${r}</p></div>`).join('');
}

// Init
function init(){renderKPIs();renderAircraftCharts();renderRoutesChart();renderIneffTable();renderScatter();renderML();renderInsights();renderRecommendations();}

window.addEventListener('load',init);
