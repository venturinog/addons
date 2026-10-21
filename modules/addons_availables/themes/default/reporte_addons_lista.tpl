{foreach from=$arrData key=k item=data}
  <div class="neo-addons-row">
    <input type="hidden" id="url_moreinfo" value="{$data.url_moreinfo|escape}"/>
    <div class="neo-addons-row-title">{$data.name|escape} - {$data.version|escape}-{$data.release|escape}</div>
    <div class="neo-addons-row-author">{$by} {$data.developed_by|escape}</div>
    <div class="neo-addons-row-icon"><img src="{$url_images|escape}/{$data.name_rpm|escape}.jpeg " width="65" height="65" alt="{$data.name|escape}" align="absmiddle" /></div>
    <div class="neo-addons-row-desc">{$data.description|escape}</div>
    <div class="neo-addons-row-location"><font style='font-weight:bold;'>{$location}: </font>{$data.location|escape}</div>
    {if $data.note}
    <div class="neo-addons-row-note"><font style='font-weight:bold;'>{$note}: </font>{$data.note|escape}</div>
    {/if}
    <div class="neo-addons-row-button">
        {* El siguiente campo hidden contiene el nombre del RPM a manipular *}
        <input type="hidden" id="name_rpm" value="{$data.name_rpm|escape}"/>
        {if $data.installed_version == ''}
            {if $data.is_commercial and $data.fecha_compra eq 0}
	    <input type="hidden" id="{$data.name_rpm|escape}_link" value="{$data.url_marketplace|escape}{$server_key|escape}&referer="/>
	    {if $data.has_trialversion eq 1}
	    <div class="neo-addons-row-button-trial-left">{$TRIAL}</div><div class="neo-addons-row-button-trial-right"><img width="17" height="17" alt="{$TRIAL|escape}" src="modules/{$module_name}/images/addons_icon_install.png"></div>
	    {/if}
            <div class="neo-addons-row-button-buy-left">{$BUY}</div>
            <div class="neo-addons-row-button-buy-right"><img src="modules/{$module_name}/images/addons_icon_buy.png" width="19" height="18" alt="{$BUY|escape}" /></div>
            {else}
            <div class="neo-addons-row-button-install-left">{$INSTALL}</div>
            <div class="neo-addons-row-button-install-right"><img src="modules/{$module_name}/images/addons_icon_install.png" width="17" height="17" alt="{$INSTALL|escape}" /></div>
            {/if}
        {else}
        {if $data.can_update}
            <div class="neo-addons-row-button-install-left tooltipInfo">{$UPDATE}{if !empty($data.upgrade_info)}<span>{$data.upgrade_info|escape}</span>{/if}</div>
            <div class="neo-addons-row-button-install-right"><img src="modules/{$module_name}/images/addons_icon_update.png" width="20" height="17" alt="{$UPDATE|escape}" /></div>
        {/if}
	<input type="hidden" id="{$data.name_rpm|escape}_installed" value="yes"/>
        <div class="neo-addons-row-button-uninstall-left">{$UNINSTALL}</div>
        <div class="neo-addons-row-button-uninstall-right"><img src="modules/{$module_name}/images/addons_icon_uninstall.png" width="17" height="17" alt="{$UNINSTALL|escape}" /></div>
	{if $data.fecha_compra eq 0 and $data.is_commercial}
	    <input type="hidden" id="{$data.name_rpm|escape}_link" value="{$data.url_marketplace|escape}{$server_key|escape}&referer="/>
	    <div class="neo-addons-row-button-buy-left">{$BUY}</div>
	    <div class="neo-addons-row-button-buy-right"><img src="modules/{$module_name}/images/addons_icon_buy.png" width="19" height="18" alt="{$BUY|escape}" /></div>
	{/if}
        {/if}
    </div>
    <div class="neo-addons-row-moreinfo">{$more_info}...</div>
  </div>
{/foreach}

<input type="hidden" name="callback" id="callback" value="" />
