from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
start = '<!-- QUANTY_PREMIUM_HORARIOS_START -->'
end = '<!-- QUANTY_PREMIUM_HORARIOS_END -->'

if start in s and end in s:
    a = s.index(start)
    b = s.index(end, a) + len(end)
    s = s[:a] + s[b:]

patch = r'''
<!-- QUANTY_PREMIUM_HORARIOS_START -->
<style>
.wrap.horarios-wide{max-width:1280px}
.qp-host{margin:0 -2px 18px;border:1px solid #1f3b59;border-radius:18px;overflow:hidden;background:#07111f;box-shadow:0 12px 34px rgba(7,17,31,.12);min-height:240px}
.qp-frame{display:block;width:100%;height:980px;border:0;background:#07111f;opacity:0;transition:opacity .18s}
.qp-loading,.qp-real-error{padding:42px 22px;text-align:center;background:#07111f;color:#8fb6d8;font-size:13px;line-height:1.55}
.qp-loading b,.qp-real-error b{display:block;color:#eaf6ff;font-size:16px;margin-bottom:7px}
.qp-real-error{color:#ffc0cc}.qp-real-error b{color:#ff9bad}
@media(max-width:760px){.wrap.horarios-wide{max-width:680px}.qp-host{margin-left:-20px;margin-right:-20px;border-radius:0;border-left:0;border-right:0}.qp-frame{height:1050px}}
</style>
<script>
(function(){
  const oldRenderHorarios=window.renderHorarios;
  window.renderHorarios=function(){
    const body=document.getElementById('sBody');
    const wrap=document.querySelector('.wrap');
    if(wrap)wrap.classList.add('horarios-wide');
    if(!body){if(oldRenderHorarios)oldRenderHorarios();return;}
    body.innerHTML='<div class="qp-host" id="qpHost"><div class="qp-loading" id="qpLoading"><b>Cargando datos reales</b>Conectando con Supabase…</div><iframe id="qpHorariosFrame" class="qp-frame" src="horarios-premium.html?real=1" title="Horarios del equipo"></iframe></div>';
    const frame=document.getElementById('qpHorariosFrame');
    const host=document.getElementById('qpHost');
    if(!frame||!host)return;
    frame.addEventListener('load',function(){
      try{
        const d=frame.contentDocument;if(!d)return;
        const top=d.querySelector('.top');if(top)top.style.display='none';
        const foot=d.querySelector('.foot');if(foot)foot.style.display='none';
        const w=d.querySelector('.wrap');if(w){w.style.maxWidth='none';w.style.padding='18px';}
        const resize=function(){try{frame.style.height=Math.max(900,d.documentElement.scrollHeight+24)+'px';}catch(e){}};
        const started=Date.now();
        const gate=setInterval(function(){
          try{
            const st=d.getElementById('status');
            const txt=st?String(st.textContent||'').trim():'';
            if(txt==='EN LÍNEA'){
              clearInterval(gate);
              const loading=document.getElementById('qpLoading');if(loading)loading.remove();
              frame.style.opacity='1';resize();setTimeout(resize,300);setTimeout(resize,1000);
              if(window.ResizeObserver)new ResizeObserver(resize).observe(d.body);
            }else if(txt==='DEMO LOCAL'||txt==='SIN CONEXIÓN'||Date.now()-started>12000){
              clearInterval(gate);
              host.innerHTML='<div class="qp-real-error"><b>Sin conexión a datos reales</b>No se muestran datos demo. Revisa Supabase y pulsa nuevamente Horarios.</div>';
            }
          }catch(e){
            clearInterval(gate);
            host.innerHTML='<div class="qp-real-error"><b>No se pudo validar la conexión</b>La malla real no se mostrará hasta confirmar Supabase.</div>';
          }
        },150);
      }catch(e){
        host.innerHTML='<div class="qp-real-error"><b>No se pudo cargar Horarios</b>El resto de Control Equipo sigue funcionando normalmente.</div>';
      }
    });
  };
  document.querySelectorAll('.stab').forEach(function(t){
    t.addEventListener('click',function(){
      const w=document.querySelector('.wrap');
      if(w&&t.dataset.s!=='horarios')w.classList.remove('horarios-wide');
    });
  });
})();
</script>
<!-- QUANTY_PREMIUM_HORARIOS_END -->
'''

if '</body>' not in s:
    raise SystemExit('No closing </body>; refusing to patch')

s = s.replace('</body>', patch + '\n</body>', 1)
p.write_text(s, encoding='utf-8')
print('Premium Horarios real-data gate prepared.')
