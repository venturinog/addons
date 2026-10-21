{* Aviso de la página. La familia de avisos del tema (STYLE.md §3.1) trae una
   variante por severidad; el icono y el título cambian con ella. *}
<div id="issabel_addons_alert" class="iss-alert iss-alert--info" style="display: none;">
    <div class="iss-alert__title"><i id="issabel_addons_alert_icon" class="ti ti-info-circle"></i> <span id="issabel_addons_alert_title"></span></div>
    <div class="iss-alert__content" id="issabel_addons_alert_text"></div>
    <div class="iss-alert__dismiss"><i class="ti ti-x" onclick="ocultar_mensaje_addons();"></i></div>
</div>

<div class="iss-form">
    <section class="iss-card">
        <div class="iss-card__header"><i class="ti ti-filter"></i> {$filter_title}</div>
        <div class="iss-card__body iss-formgrid">
            <div class="iss-field">
                <span class="iss-field__label">{$filter_by}</span>
                <span class="iss-field__control">
                    <select id="filter_by" class="form-select" name="filter_by" onchange="javascript:do_listarAddons(null)">
                        <option value="available">{$available}</option>
                        <option value="installed">{$installed}</option>
                        <option value="purchased">{$purchased}</option>
                        <option value="update_available">{$update_available}</option>
                    </select>
                </span>
            </div>
            <div class="iss-field">
                <span class="iss-field__label">{$name}</span>
                <span class="iss-field__control">
                    <div class="iss-addons__search">
                        <input type="text" id="filter_namerpm" class="form-control" value="" name="filter_namerpm" onkeypress="javascript:keyPressed(event)">
                        <button class="btn btn-outline-secondary" type="button" onclick="javascript:do_listarAddons(null)" aria-label="{$search}" title="{$search}">
                            <i class="ti ti-search"></i>
                        </button>
                    </div>
                </span>
            </div>
        </div>
    </section>
</div>

<div id="addonlist" class="iss-addons__list"></div>

<nav class="iss-addons__pager">
    <div class="iss-grid__nav">
        <button type="button" class="btn btn-outline-secondary btn-sm" id="imgPrimero" aria-label="{$lbl_start}" title="{$lbl_start}"><i class="ti ti-chevrons-left"></i></button>
        <button type="button" class="btn btn-outline-secondary btn-sm" id="imgAnterior" aria-label="{$lbl_previous}" title="{$lbl_previous}"><i class="ti ti-chevron-left"></i></button>
        <span class="iss-addons__range">{$showing} <span id="addonlist_start_range">?</span> - <span id="addonlist_end_range">?</span> {$of} <span id="addonlist_total">?</span></span>
        <button type="button" class="btn btn-outline-secondary btn-sm" id="imgSiguiente" aria-label="{$lbl_next}" title="{$lbl_next}"><i class="ti ti-chevron-right"></i></button>
        <button type="button" class="btn btn-outline-secondary btn-sm" id="imgFinal" aria-label="{$lbl_end}" title="{$lbl_end}"><i class="ti ti-chevrons-right"></i></button>
    </div>
</nav>

{* Progreso de la transacción. El componente es el del tema; su JavaScript no
   está disponible dentro del iframe del módulo, así que el propio script del
   módulo lo muestra y lo esconde a mano (igual que el modal del CDR). *}
<div class="modal" id="issabel_addons_modal" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="issabel_addons_modal_title"></h5>
                <button type="button" class="btn-close" id="issabel_addons_modal_close" aria-label="{$cancel}"></button>
            </div>
            <div class="modal-body">
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" id="issabel_addons_progress" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <div class="iss-addons__progress">
                    <span class="iss-addons__progress-value" id="issabel_addons_progress_value">0%</span>
                    <span id="feedback"></span>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-outline-danger" id="issabel_addons_cancel">{$cancel_transaction}</button>
            </div>
        </div>
    </div>
</div>
<div class="modal-backdrop" id="issabel_addons_backdrop" style="display: none;"></div>

<script type="text/javascript">
var issabel_addons_titulos = {$ADDONS_ALERT_TITLES};
var issabel_addons_mensajes = {$ADDONS_MESSAGES};
var cancel_confirm = {$ADDONS_CANCEL_CONFIRM};
</script>
