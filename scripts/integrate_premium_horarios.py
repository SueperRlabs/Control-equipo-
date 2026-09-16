from pathlib import Path

# 1) Keep the Control Equipo core intact and only append the Horarios visual shell.
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
.qp-host{margin:0 -2px 18px;border:1px solid #1f3b59;border-radius:18px;overflow:hidden;background:#07111f;box-shadow:0 12px 34px rgba(7,17,31,.12)}
.qp-frame{display:block;width:100%;height:980px;border:0;background:#07111f}
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
    body.innerHTML='<div class="qp-host"><iframe id="qpHorariosFrame" class="qp-frame" src="horarios-premium.html?real=1" title="Horarios del equipo"></iframe></div>';
    const frame=document.getElementById('qpHorariosFrame');
    if(!frame)return;
    frame.addEventListener('load',function(){
      try{
        const d=frame.contentDocument;if(!d)return;
        const top=d.querySelector('.top');if(top)top.style.display='none';
        const foot=d.querySelector('.foot');if(foot)foot.style.display='none';
        const w=d.querySelector('.wrap');if(w){w.style.maxWidth='none';w.style.padding='18px';}
        const resize=function(){try{frame.style.height=Math.max(900,d.documentElement.scrollHeight+24)+'px';}catch(e){}};
        resize();setTimeout(resize,250);setTimeout(resize,900);
        if(window.ResizeObserver)new ResizeObserver(resize).observe(d.body);
      }catch(e){}
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

# 2) Embedded Horarios must be REAL ONLY. The standalone ?demo=1 remains available
# for development, but Control Equipo loads ?real=1 and must never silently show fake data.
h = Path('horarios-premium.html')
hs = h.read_text(encoding='utf-8')
force_line = "const FORCE_DEMO=new URLSearchParams(location.search).get('demo')==='1';"
real_line = "const REAL_ONLY=new URLSearchParams(location.search).get('real')==='1';"
if real_line not in hs:
    if force_line not in hs:
        raise SystemExit('FORCE_DEMO marker missing; refusing to patch premium view')
    hs = hs.replace(force_line, force_line + '\n' + real_line, 1)

old_catch = "}catch(e){activarDemo('Backend no disponible; se activó automáticamente la demo.')}"
new_catch = """}catch(e){
    if(REAL_ONLY){
      DEMO=false;
      const st=document.getElementById('status');st.textContent='SIN CONEXIÓN';st.classList.remove('demo');
      document.getElementById('sub').textContent='No fue posible leer los datos reales';
      document.getElementById('notice').innerHTML='<div class=\"notice\"><b>Sin conexión a datos reales.</b> No se muestran datos demo. Pulsa Actualizar cuando vuelva Supabase.</div>';
      document.getElementById('table').innerHTML='<tbody><tr><td style=\"padding:28px;text-align:center;color:#8fb6d8\">Esperando conexión con Supabase…</td></tr></tbody>';
      document.getElementById('editor').classList.add('hide');
    }else activarDemo('Backend no disponible; se activó automáticamente la demo.')
  }"""
if 'No se muestran datos demo' not in hs:
    if old_catch not in hs:
        raise SystemExit('Premium fallback catch marker missing; refusing to patch')
    hs = hs.replace(old_catch, new_catch, 1)

hs = hs.replace('En modo demo los cambios quedan guardados solo en este navegador. En modo real se usan los mismos turnos de Control Equipo.',
                'Los cambios de esta vista integrada se guardan en los mismos turnos reales de Control Equipo.')
h.write_text(hs, encoding='utf-8')
print('Premium Horarios integration prepared in real-only mode.')
