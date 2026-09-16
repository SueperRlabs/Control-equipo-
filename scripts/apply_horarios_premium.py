from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

MARK = '/* QUANTY HORARIOS PREMIUM */'
if MARK in s:
    print('Premium horarios already applied')
    raise SystemExit(0)

premium_css = r'''

  /* QUANTY HORARIOS PREMIUM */
  .hp-shell{background:linear-gradient(180deg,#07111f,#0a1726 60%,#07111f);border:1px solid #1f3b59;border-radius:18px;padding:16px;margin-bottom:14px;color:#eaf6ff;overflow:hidden;}
  .hp-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:14px;flex-wrap:wrap;}
  .hp-eyebrow{font-size:10px;font-weight:800;letter-spacing:.16em;color:#42e8ff;text-transform:uppercase;}
  .hp-title{font-size:20px;font-weight:800;letter-spacing:-.02em;margin-top:3px;}
  .hp-sub{font-size:12px;color:#8fb6d8;margin-top:3px;}
  .hp-badge{font-size:10px;font-weight:800;letter-spacing:.08em;border:1px solid #245775;background:#0d2235;color:#7deeff;padding:7px 10px;border-radius:999px;white-space:nowrap;}
  .hp-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:14px;}
  .hp-kpi{background:#0d1b2a;border:1px solid #1f3b59;border-radius:13px;padding:10px 11px;min-width:0;}
  .hp-kpi b{display:block;font-size:18px;color:#eaf6ff;line-height:1.1;}
  .hp-kpi span{display:block;color:#8fb6d8;font-size:9.5px;margin-top:4px;}
  .hp-nav{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px;}
  .hp-nav .arrow{background:#0d1b2a;border-color:#1f3b59;color:#8fb6d8;}
  .hp-nav .lbl{color:#eaf6ff;font-weight:700;font-size:13px;}
  .hp-tablewrap{overflow:auto;border:1px solid #1f3b59;border-radius:14px;background:#0d1b2a;margin-bottom:14px;}
  .hp-table{border-collapse:separate;border-spacing:0;min-width:920px;width:100%;font-size:12px;}
  .hp-table th{position:sticky;top:0;background:#0b1827;color:#8fb6d8;padding:10px 8px;text-align:center;border-bottom:1px solid #1f3b59;font-size:9px;letter-spacing:.07em;text-transform:uppercase;z-index:1;}
  .hp-table th:first-child{left:0;z-index:2;text-align:left;min-width:170px;}
  .hp-table td{padding:8px;border-bottom:1px solid rgba(31,59,89,.62);border-right:1px solid rgba(31,59,89,.45);color:#eaf6ff;text-align:center;white-space:nowrap;}
  .hp-table td:first-child{position:sticky;left:0;background:#0d1b2a;text-align:left;z-index:1;font-weight:650;}
  .hp-cell{display:inline-flex;align-items:center;justify-content:center;min-height:32px;padding:6px 8px;border-radius:8px;background:#10243a;color:#dff7ff;font-variant-numeric:tabular-nums;cursor:pointer;border:1px solid transparent;}
  .hp-cell:hover{border-color:#2d5a7f;}
  .hp-cell.sel{border-color:#42e8ff;box-shadow:0 0 0 1px rgba(66,232,255,.18) inset;}
  .hp-cell.libre{background:#24303a;color:#a9b8c5;}
  .hp-cell.vac{background:#3c2d14;color:#ffd77a;}
  .hp-total{font-weight:800;color:#80f0b2!important;}
  .hp-editor{background:#0d1b2a;border:1px solid #1f3b59;border-radius:14px;padding:14px;margin-top:12px;}
  .hp-editor .card-h{color:#8fb6d8;}
  .hp-editor .turno{border-bottom-color:#1f3b59;}
  .hp-editor .nm{color:#eaf6ff;}
  .hp-editor .hrs{color:#8fb6d8;}
  .hp-editor input{background:#071725;border-color:#294864;color:#eaf6ff;}
  .hp-editor .libre-btn{background:#0b1827;border-color:#294864;color:#8fb6d8;}
  .hp-editor .libre-btn.on{background:#24303a;color:#d8e5ef;border-color:#50687a;}
  .hp-editor .btn{background:#0f766e;}
  .hp-editor .btn.sec{background:#0b1827;color:#dce9f2;border-color:#294864;}
  .hp-footnote{font-size:10.5px;color:#789bb6;line-height:1.5;margin-top:10px;}
  @media(max-width:760px){.hp-shell{padding:12px}.hp-kpis{grid-template-columns:repeat(2,1fr)}.hp-title{font-size:18px}.hp-table th:first-child{min-width:135px}.hp-table{min-width:820px}}
'''

s = s.replace('</style>', premium_css + '\n</style>', 1)

new_render = r'''function horasEfectivasVisual(t){
  if(!turnoActivo(t)||!t.entrada||!t.salida)return 0;
  return Math.max(0,Math.round((horasTurno(t.entrada,t.salida)-1)*100)/100);
}
function horasSemanaVisual(empId,lunesStr){
  return diasDeSemana(lunesStr).reduce((acc,f)=>acc+horasEfectivasVisual(turnoDe(TURNOS,empId,f)),0);
}
function renderHorarios(){
  if(!EQ.length){
    document.getElementById('sBody').innerHTML='<div class="card"><div class="empty">Todavía no hay personas en el equipo.<br>Agrégalas en Ajustes para asignarles turnos.</div></div>';
    return;
  }
  const dias=diasDeSemana(LUNES), hoy=dateKey();
  if(!dias.includes(DIA_SEL))DIA_SEL=dias[0];
  const anio=Number(FECHA.slice(0,4)), mes=Number(FECHA.slice(5,7))-1;
  const activos=EQ.filter(p=>turnoActivo(turnoDe(TURNOS,p.id,DIA_SEL))).length;
  const libres=EQ.filter(p=>{const t=turnoDe(TURNOS,p.id,DIA_SEL);return !!(t&&t.libre);}).length;
  const vacantes=EQ.filter(p=>{const t=turnoDe(TURNOS,p.id,DIA_SEL);return !!(t&&t.vacante);}).length;
  const hefect=EQ.reduce((a,p)=>a+horasEfectivasVisual(turnoDe(TURNOS,p.id,DIA_SEL)),0);

  document.getElementById('sBody').innerHTML=
  '<div class="hp-shell">'+
    '<div class="hp-top"><div><div class="hp-eyebrow">QUANTY · CONTROL DE EQUIPO</div>'+
      '<div class="hp-title">Malla semanal</div><div class="hp-sub">'+esc(CFG.nombre)+' · '+rotuloSemana(LUNES)+' · 1 h de colación</div></div>'+
      '<div class="hp-badge">MOTOR INTACTO</div></div>'+
    '<div class="hp-kpis">'+
      '<div class="hp-kpi"><b>'+EQ.length+'</b><span>Equipo</span></div>'+
      '<div class="hp-kpi"><b>'+activos+'</b><span>Programados '+DIAS[(parseKey(DIA_SEL).getDay()+6)%7]+'</span></div>'+
      '<div class="hp-kpi"><b>'+libres+'</b><span>Libres</span></div>'+
      '<div class="hp-kpi"><b>'+hefect.toFixed(1)+' h</b><span>Horas efectivas del día</span></div></div>'+
    '<div class="hp-nav"><button class="arrow" onclick="semana(-7)">‹</button><div class="lbl">'+rotuloSemana(LUNES)+'</div><button class="arrow" onclick="semana(7)">›</button></div>'+
    '<div class="hp-tablewrap"><table class="hp-table"><thead><tr><th>Vendedor/a</th>'+
      dias.map((f,i)=>'<th>'+DIAS[i]+' '+parseKey(f).getDate()+'</th>').join('')+'<th>Total</th></tr></thead><tbody>'+
      EQ.map(p=>'<tr><td>'+esc(p.nombre)+'</td>'+dias.map(f=>{const t=turnoDe(TURNOS,p.id,f);let txt='—',cl='';if(t&&t.libre){txt='LIBRE';cl=' libre';}else if(t&&t.vacante){txt='VACANTE';cl=' vac';}else if(t&&t.entrada){txt=esc(t.entrada+'–'+(t.salida||'—'));}return '<td><span class="hp-cell'+cl+(f===DIA_SEL?' sel':'')+'" onclick="selDia(\''+f+'\')">'+txt+'</span></td>';}).join('')+'<td class="hp-total">'+horasSemanaVisual(p.id,LUNES).toFixed(1)+' h</td></tr>').join('')+
      '</tbody></table></div>'+
    '<div class="hp-footnote">Horas efectivas visuales descuentan 1 hora de colación por cada turno trabajado. Los datos y las funciones de guardar/copiar siguen usando el mismo motor y la misma base.</div>'+
  '</div>'+
  '<div class="hp-editor">'+
    '<div class="card-h">Editar '+rotuloFecha(DIA_SEL)+'<span>Horas exactas · colación 1 h · '+activos+' programados'+(vacantes?' · '+vacantes+' vacante(s)':'')+'</span></div>'+
    EQ.map(p=>{const t=turnoDe(TURNOS,p.id,DIA_SEL)||{};const h=horasEfectivasVisual(t);return '<div class="turno" data-emp="'+p.id+'" data-vac="'+(t.vacante?'1':'')+'"><div class="turno-top"><div class="nm">'+esc(p.nombre)+'</div><span class="hrs">'+(t.libre?'libre':t.vacante?'vacante':(h?h.toFixed(1)+' h efect.':''))+'</span>'+(t.vacante?'<button class="libre-btn on" onclick="liberarVacante(this)">Vacante ✕</button>':'')+'<button class="libre-btn'+(t.libre?' on':'')+'" onclick="toggleLibre(this)">Libre</button></div><div class="turno-in"'+(t.libre?' style="opacity:.35;pointer-events:none"':'')+'><input type="time" data-f="entrada" value="'+(t.entrada||'')+'"><span class="sep">a</span><input type="time" data-f="salida" value="'+(t.salida||'')+'"></div></div>';}).join('')+
    '<div id="hMsg" style="margin-top:14px"></div><button class="btn" onclick="guardarTurnos()">Guardar este día</button><div class="btn-row"><button class="btn sec" onclick="copiarASemana()">Copiar a la semana</button><button class="btn sec" onclick="copiarSemanaAnterior()">Traer semana previa</button></div>'+
  '</div>'+
  '<div class="card"><div class="card-h">Resumen mensual<span>'+MESES[mes]+' '+anio+'</span></div><table><thead><tr><th>Persona</th><th>Libres</th><th>Horas cargadas</th></tr></thead><tbody>'+EQ.map(p=>'<tr><td>'+esc(p.nombre)+'</td><td>'+diasLibresMes(TURNOS,p.id,anio,mes)+'</td><td><b>'+horasMes(TURNOS,p.id,anio,mes).toFixed(1)+' h</b></td></tr>').join('')+'</tbody></table><div class="msg info" style="margin-top:12px;margin-bottom:0">Este resumen conserva el cálculo original del sistema.</div></div>';
}
'''

pattern = re.compile(r'function renderHorarios\(\)\{.*?\n\}\nasync function semana\(n\)', re.S)
m = pattern.search(s)
if not m:
    raise SystemExit('renderHorarios block not found')
s = s[:m.start()] + new_render + 'async function semana(n)' + s[m.end():]

p.write_text(s, encoding='utf-8')
print('Premium horarios applied safely')
