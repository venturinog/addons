{foreach from=$arrData key=k item=data}
  <article class="iss-card iss-addons__item">
    <div class="iss-card__body iss-addons__item-body">
      <img class="iss-addons__icon" src="{$url_images|escape}/{$data.name_rpm|escape}.jpeg" width="65" height="65" alt="{$data.name|escape}" onerror="this.style.visibility='hidden';">
      <div class="iss-addons__main">
        <div class="iss-addons__title">
          <span class="iss-addons__name">{$data.name|escape}</span>
          <span class="iss-addons__version">{$data.version|escape}-{$data.release|escape}</span>
        </div>
        <div class="iss-addons__author">{$by} {$data.developed_by|escape}</div>
        <p class="iss-addons__desc">{$data.description|escape}</p>
        <div class="iss-addons__meta">
          <div class="iss-addons__metaitem"><span class="iss-addons__metalabel">{$location}:</span> {$data.location|escape}</div>
          {if $data.note}
          <div class="iss-addons__metaitem"><span class="iss-addons__metalabel">{$note}:</span> {$data.note|escape}</div>
          {/if}
        </div>
        <a class="iss-addons__moreinfo" href="{$data.url_moreinfo|escape}" target="_blank" rel="noopener">{$more_info} <i class="ti ti-external-link"></i></a>
      </div>
      <div class="iss-addons__actions">
        {* El nombre del RPM a manipular viaja en el propio boton. *}
        {if $data.installed_version == ''}
            {if $data.is_commercial and $data.fecha_compra eq 0}
            <input type="hidden" id="{$data.name_rpm|escape}_link" value="{$data.url_marketplace|escape}{$server_key|escape}&amp;referer="/>
            {if $data.has_trialversion eq 1}
            <button type="button" class="btn btn-outline-secondary iss-addons__action" data-accion="install" data-name-rpm="{$data.name_rpm|escape}">
                <i class="ti ti-player-play"></i> {$TRIAL}
            </button>
            {/if}
            <button type="button" class="btn btn-outline-success iss-addons__action" data-accion="buy" data-name-rpm="{$data.name_rpm|escape}">
                <i class="ti ti-shopping-cart"></i> {$BUY}
            </button>
            {else}
            <button type="button" class="btn btn-outline-primary iss-addons__action" data-accion="install" data-name-rpm="{$data.name_rpm|escape}">
                <i class="ti ti-download"></i> {$INSTALL}
            </button>
            {/if}
        {else}
        {if $data.can_update}
            <button type="button" class="btn btn-outline-primary iss-addons__action iss-addons__tooltip" data-accion="install" data-name-rpm="{$data.name_rpm|escape}">
                <i class="ti ti-refresh"></i> {$UPDATE}
                {if !empty($data.upgrade_info)}<span class="iss-addons__tip">{$data.upgrade_info|escape}</span>{/if}
            </button>
        {/if}
        <input type="hidden" id="{$data.name_rpm|escape}_installed" value="yes"/>
        <button type="button" class="btn btn-outline-danger iss-addons__action" data-accion="uninstall" data-name-rpm="{$data.name_rpm|escape}">
            <i class="ti ti-trash"></i> {$UNINSTALL}
        </button>
        {if $data.fecha_compra eq 0 and $data.is_commercial}
        <input type="hidden" id="{$data.name_rpm|escape}_link" value="{$data.url_marketplace|escape}{$server_key|escape}&amp;referer="/>
        <button type="button" class="btn btn-outline-success iss-addons__action" data-accion="buy" data-name-rpm="{$data.name_rpm|escape}">
            <i class="ti ti-shopping-cart"></i> {$BUY}
        </button>
        {/if}
        {/if}
      </div>
    </div>
  </article>
{/foreach}

<input type="hidden" name="callback" id="callback" value="" />
