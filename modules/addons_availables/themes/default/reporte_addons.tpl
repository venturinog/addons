{* Aviso de la página. La familia de avisos del tema (STYLE.md §3.1) trae una
   variante por severidad; el icono y el título cambian con ella. *}
<div id="issabel_addons_alert" class="iss-alert iss-alert--info" style="display: none;">
    <div class="iss-alert__title"><i id="issabel_addons_alert_icon" class="ti ti-info-circle"></i> <span id="issabel_addons_alert_title"></span></div>
    <div class="iss-alert__content" id="issabel_addons_alert_text"></div>
    <div class="iss-alert__dismiss"><i class="ti ti-x" onclick="ocultar_mensaje_addons();"></i></div>
</div>
  <div class="neo-addons-header-row">
    <div class="neo-addons-header-row-filter">
      {$filter_by}:
      <select id="filter_by" class="neo-addons-header-row-select" name="filter_by" onchange="javascript:do_listarAddons(null)">
        <option value="available">{$available}</option>
        <option value="installed">{$installed}</option>
        <option value="purchased">{$purchased}</option>
        <option value="update_available">{$update_available}</option>
      </select>
    </div>
    <div class="neo-addons-header-row-filter">
      <span style="vertical-align:top;">{$name}:</span>
      <input type="text" id="filter_namerpm" value="" name="filter_namerpm" onkeypress="javascript:keyPressed(event)">
      <a onclick="javascript:do_listarAddons(null)" href="#">
      <img width="19" height="21" border="0" align="absmiddle" src="modules/{$module_name}/images/searchw.png" alt="">
      </a>
    </div>
    <div class="neo-addons-header-row-navigation">
        <img id="imgPrimero" style="cursor: pointer;" src="modules/{$module_name}/images/table-arrow-first.gif" width="16" height="16" alt='{$lblStart}' align='absmiddle' />
        <img id="imgAnterior"  style="cursor: pointer;" src="modules/{$module_name}/images/table-arrow-previous.gif" width="16" height="16" alt='{$lblPrevious}' align='absmiddle' />
        ({$showing} <span id="addonlist_start_range">?</span> - <span id="addonlist_end_range">?</span> {$of} <span id="addonlist_total">?</span>)
        <img id="imgSiguiente" style="cursor: pointer;" src="modules/{$module_name}/images/table-arrow-next.gif" width="16" height="16" alt='{$lblNext}' align='absmiddle' />
        <img id="imgFinal" style="cursor: pointer;" src="modules/{$module_name}/images/table-arrow-last.gif" width="16" height="16" alt='{$lblEnd}' align='absmiddle' />
    </div>
  </div>
<div id="addonlist">
<div style="text-align: center; padding: 40px;">
<img src="images/loading.gif" />
</div>
</div>
     <div id="footer" style="background: url(../../../images/addons_header_row_bg.png) repeat-x top; width: 100%; height:40px;"  >
     <div class="neo-addons-header-row-navigation">
        <img id="imgPrimeroFooter" style="cursor: pointer;" src="modules/{$module_name}/images/table-arrow-first.gif" width="16" height="16" alt='{$lblStart}' align='absmiddle' />
        <img id="imgAnteriorFooter"  style="cursor: pointer;" src="modules/{$module_name}/images/table-arrow-previous.gif" width="16" height="16" alt='{$lblPrevious}' align='absmiddle' />
        ({$showing} <span id="addonlist_start_range_footer">?</span> - <span id="addonlist_end_range_footer">?</span> {$of} <span id="addonlist_total_footer">?</span>)
        <img id="imgSiguienteFooter" style="cursor: pointer;" src="modules/{$module_name}/images/table-arrow-next.gif" width="16" height="16" alt='{$lblNext}' align='absmiddle' />
        <img id="imgFinalFooter" style="cursor: pointer;" src="modules/{$module_name}/images/table-arrow-last.gif" width="16" height="16" alt='{$lblEnd}' align='absmiddle' />
    </div>
    </div>
<!-- Neo Progress Bar -->
<div class="neo-modal-box">
  <div id="container">
    <div class="neo-progress-bar-percentage"><span class="neo-progress-bar-percentage-tag"></span></div>
    <div class="neo-progress-bar"><div class="neo-progress-bar-progress"></div></div>
    <span class="neo-progress-bar-label"><img src="images/loading2.gif" align="absmiddle" />&nbsp;<span id="feedback"></span></span>
    <div class="neo-progress-bar-title"></div>
    <div class="neo-progress-bar-close"></div>
  </div>
</div>
<div class="neo-modal-blockmask"></div>
<script type="text/javascript">
var issabel_addons_titulos = {$ADDONS_ALERT_TITLES};
</script>
