var module_name = "addons_availables";

// Variables para paginación
var addonlist_offset = null;
var addonlist_limit = null;
var addonlist_total = null;

// Variable para manejar el llamado a la función do_checkStatus()
var intervalCheckStatus = null;

var dialogo_progreso_abierto = false;
var transaction_in_progress = false;
var checking_dependencies = false;
var transaction_cancelled = false;
var refer = document.URL;

/* El siguiente objeto es el estado de la interfaz del Addon Market. Al comparar
 * este objeto con los cambios de estado producto de la revisión periódica del
 * demonio actualizador, consigue detectar los cambios requeridos a la interfaz
 * sin tener que recurrir a llamadas repetidas al servidor.
 * Este objeto se actualiza en do_checkStatus() */
var estadoCliente =
{
	// Este estado inicializado representa una sistema ocioso
	name_rpm:	null,	// NULL para sistema ocioso, o el RPM que se opera
	fraccion:	0		// Fracción de completado, rango 0 hasta 1000.
};

/* Nombre de un RPM de addon. Es la misma regla que aplica el servidor en
 * validAddonName() (STYLE.md §5): el servidor sigue siendo la fuente de la
 * verdad, esto solo evita un viaje de ida y vuelta. */
function validAddonName(name_rpm)
{
	return /^[a-zA-Z0-9]+(-[a-zA-Z0-9_]+)?$/.test(name_rpm || '');
}

$(document).ready(function() {
	$('#imgPrimero').click(function () {
		if (addonlist_offset != null && addonlist_offset > 0)
			do_listarAddons(0);
        });
	$('#imgAnterior').click(function () {
		if (addonlist_offset != null && addonlist_offset >= addonlist_limit)
			do_listarAddons(addonlist_offset - addonlist_limit);
	});
	$('#imgSiguiente').click(function () {
		if (addonlist_offset != null && addonlist_offset + addonlist_limit < addonlist_total)
			do_listarAddons(addonlist_offset + addonlist_limit);
	});
	$('#imgFinal').click(function () {
		if (addonlist_offset != null) {
			var offsetfinal = addonlist_total - (addonlist_total % addonlist_limit);
			if (offsetfinal == addonlist_total)
				offsetfinal -= addonlist_limit;
			if (offsetfinal > addonlist_offset)
				do_listarAddons(offsetfinal);
		}
	});
	$('#issabel_addons_cancel').click(function () {
		if (confirm(cancel_confirm))
			cancelTransaction();
	});
	$('#issabel_addons_modal_close').click(function () {
		issabelAddonsModal('hide');
	});

	do_listarAddons(null);
});

/**
 * Procedimiento para listar los addons vía AJAX. Inmediatamente luego de que
 * se recibe una respuesta correcta, se invoca de inmediato do_checkStatus() que
 * actualiza la interfaz para que se corresponda al estado del sistema de
 * actualización.
 *
 * @param int	list_offset	Offset desde el cual iniciar el listado
 *
 * @return void
 */
function do_listarAddons(list_offset)
{
	loadingAddons();
	var filter_by = $('#filter_by').val();
	var filter_nameRpm = $('#filter_namerpm').val();
	addonlist_offset = null;
	addonlist_limit = null;
	addonlist_total = null;
	$.post('index.php?menu=' + module_name + '&rawmode=yes', {
		menu:		module_name,
		rawmode:	'yes',
		action:		'listarAddons',
		offset:		list_offset,
		filter_by:	filter_by,
		filter_nameRpm: filter_nameRpm
	},
	function (respuesta) {
		if (respuesta['action'] == 'error') {
			mostrar_mensaje(respuesta['message'],'error');
		} else {
			cancel_confirm = respuesta['cancel_confirm'];
			if(respuesta['catalogue_empty']){
			    /* El catálogo del marketplace está vacío para la versión de
			     * Issabel de esta instalación. El aviso lo explica; el
			     * área de lista se deja vacía para no repetir el aviso. */
			    $('#addonlist').empty();
			    mostrar_mensaje(respuesta['catalogue_empty_message'],'info');
			}
			else if(respuesta['empty_addons']){
			    $('#addonlist')
				.empty()
				.append($('<div class="iss-addons__empty"></div>').text(respuesta['empty_addons']));
			}
			else{
			    $('#addonlist')
				    .empty()
				    .append(respuesta['addonlist_html']);
			}
			addonlist_offset = respuesta['offset'];
			addonlist_limit = respuesta['limit'];
			addonlist_total = respuesta['total'];
			actualizar_paginacion();
			enlazar_botones_addon();
			// Iniciar la revisión del status de la instalación
			do_checkStatus();
		}
	});
}

/* Estado de los botones de la paginación: se deshabilitan los que no
 * llevan a ninguna página, en vez de atenuarlos. */
function actualizar_paginacion()
{
	var offsetfinal = addonlist_total - (addonlist_total % addonlist_limit);

	$('#imgPrimero').prop('disabled', addonlist_offset == null || addonlist_offset <= 0);
	$('#imgAnterior').prop('disabled', addonlist_offset == null || addonlist_offset < addonlist_limit);
	$('#imgSiguiente').prop('disabled', addonlist_offset == null || addonlist_offset + addonlist_limit >= addonlist_total);
	$('#imgFinal').prop('disabled', addonlist_offset == null || offsetfinal <= addonlist_offset);

	if (addonlist_total == 0)
		$('#addonlist_start_range').text(0);
	else
		$('#addonlist_start_range').text(addonlist_offset + 1);
	$('#addonlist_total').text(addonlist_total);
	$('#addonlist_end_range').text(
			(addonlist_offset + addonlist_limit >= addonlist_total)
			? addonlist_total
			: addonlist_offset + addonlist_limit);
}

/* Engancha los botones de cada addon. El nombre del RPM viaja en el propio
 * boton (data-name-rpm), de modo que no hay que subir por el DOM ni buscar
 * un campo oculto que se repite en todas las filas. */
function enlazar_botones_addon()
{
	$('.iss-addons__action').off('click');
	$('.iss-addons__action').on('click', function () {
		var name_rpm = $(this).data('name-rpm');
		var accion = $(this).data('accion');

		if (!validAddonName(name_rpm)) {
			mostrar_mensaje(issabel_addons_titulos.error, 'error');
			return;
		}

		estadoCliente.name_rpm = name_rpm;
		$('body').css('cursor','wait');

		if (accion == 'uninstall')
			do_iniciarUninstall();
		else if (accion == 'buy')
			checkServerID(true);
		else
			checkServerID(false);
	});
}

function checkServerID(isPurchase)
{
    $.get('index.php',{
        menu:       'registration',
        action:     'isRegistered',
        rawmode:    'yes'
    }, function(response) {
        var arrData = response.message;

        $('body').css('cursor','default');

        if(arrData["registered"]=="yes-all"){
            if(isPurchase)
                do_checkDependencies(null);
            else
                do_iniciarInstallUpdate();
        } else{
            var callback = (isPurchase) ? "do_checkDependencies" : "do_iniciarInstallUpdate";
            $('#callback').val(callback);
            showPopupCloudLogin('',540,335);
        }
    });
}

function keyPressed(e)
{
    var keycode;
    if (window.event) keycode = window.event.keyCode;
    else if (e) keycode = e.which;
    else return true;
    if(keycode == 13){
	do_listarAddons(null);
	return false;
    }
}

/* Aviso de la página. La familia de avisos del tema (STYLE.md §3.1) trae una
 * variante por severidad, así que el icono y el título se eligen con ella.
 * El texto se inserta como texto plano: lo que llega aquí puede venir del
 * demonio actualizador. */
var issabel_addons_alert_timer = null;

function mostrar_mensaje(mensaje, tipo)
{
    if (tipo !== 'error' && tipo !== 'success' && tipo !== 'warning' && tipo !== 'info')
        tipo = 'info';

    var iconos = {
        error:   'ti-alert-triangle',
        success: 'ti-circle-check',
        warning: 'ti-alert-circle',
        info:    'ti-info-circle'
    };

    var alerta = $('#issabel_addons_alert');
    alerta.removeClass('iss-alert--error iss-alert--success iss-alert--warning iss-alert--info');
    alerta.addClass('iss-alert--' + tipo);

    $('#issabel_addons_alert_icon')
        .removeClass('ti-alert-triangle ti-circle-check ti-alert-circle ti-info-circle')
        .addClass(iconos[tipo]);

    $('#issabel_addons_alert_title').text(issabel_addons_titulos[tipo]);
    $('#issabel_addons_alert_text').text(mensaje);

    alerta.stop(true, true).fadeIn('slow');
    if (issabel_addons_alert_timer) clearTimeout(issabel_addons_alert_timer);
    issabel_addons_alert_timer = setTimeout(function () {
        alerta.fadeOut();
    }, 10000);
}

function ocultar_mensaje_addons()
{
    if (issabel_addons_alert_timer) clearTimeout(issabel_addons_alert_timer);
    $('#issabel_addons_alert').stop(true, true).fadeOut();
}

function do_iniciarCompra()
{
	var link = $('#'+estadoCliente.name_rpm+'_link').val();
	location.href = link;
}

function do_iniciarInstallUpdate()
{
	$.post('index.php?menu=' + module_name + '&rawmode=yes', {
		menu:		module_name,
		rawmode:	'yes',
		action:		'iniciarInstallUpdate',
		name_rpm:	estadoCliente.name_rpm
	},
	function (respuesta) {
		$('body').css('cursor','default');
		if(respuesta["db_error"])
		    mostrar_mensaje(respuesta["db_error"],'error');
		else if(respuesta["error"]){
		    mostrar_mensaje(respuesta["error"],'error');
		    do_checkStatus();
		}
		else if(!respuesta || respuesta["status"] === undefined){
		    /* La respuesta no es la que se espera: el servidor no ha podido
		     * hablar con el demonio actualizador. Mejor decirlo que dejar el
		     * modal de progreso congelado en 0%. */
		    mostrar_mensaje(issabel_addons_titulos.service_down,'error');
		}
		else{
		    transaction_in_progress = true;
		    mostrar_dialogo_progreso();
		    $("#issabel_addons_modal_title").text(respuesta["title"]+" "+estadoCliente.name_rpm);
		    intervalCheckStatus = setInterval("do_checkStatus()",1000);
		}
	});
}

function do_iniciarUninstall()
{
	$.post('index.php?menu=' + module_name + '&rawmode=yes', {
		menu:		module_name,
		rawmode:	'yes',
		action:		'iniciarUninstall',
		name_rpm:	estadoCliente.name_rpm
	},
	function (respuesta) {
		$('body').css('cursor','default');
		if(respuesta["db_error"])
		    mostrar_mensaje(respuesta["db_error"],'error');
		else if(respuesta["error"]){
		    mostrar_mensaje(respuesta["error"],'error');
		    do_checkStatus();
		}
		else if(!respuesta || respuesta["status"] === undefined){
		    /* La respuesta no es la que se espera: el servidor no ha podido
		     * hablar con el demonio actualizador. Mejor decirlo que dejar el
		     * modal de progreso congelado en 0%. */
		    mostrar_mensaje(issabel_addons_titulos.service_down,'error');
		}
		else{
		    transaction_in_progress = true;
		    mostrar_dialogo_progreso();
		    $("#issabel_addons_modal_title").text(respuesta["title"]+" "+estadoCliente.name_rpm);
		    intervalCheckStatus = setInterval("do_checkStatus()",1000);
		}
	});
}

/* El modal es el del tema, pero su JavaScript no se carga dentro del iframe
 * del módulo: se muestra y se esconde a mano, igual que hace el modal del
 * CDR (reports/modules/cdrreport/themes/default/js/javascript.js). */
function issabelAddonsModal(accion)
{
    var modal = document.getElementById('issabel_addons_modal');
    var backdrop = document.getElementById('issabel_addons_backdrop');
    if (!modal) return;

    var api = null;
    if (window.bootstrap && window.bootstrap.Modal) {
        api = window.bootstrap.Modal;
    } else if (window.tabler && window.tabler.bootstrap && window.tabler.bootstrap.Modal) {
        api = window.tabler.bootstrap.Modal;
    } else if (window.tabler && window.tabler.Modal) {
        api = window.tabler.Modal;
    }

    if (api) {
        var inst = api.getOrCreateInstance(modal);
        if (accion === 'hide') inst.hide(); else inst.show();
        return;
    }
    if ($.fn.modal) {
        $(modal).modal(accion);
        return;
    }
    if (accion === 'hide') {
        modal.classList.remove('show');
        modal.style.display = 'none';
        if (backdrop) {
            backdrop.classList.remove('show');
            backdrop.style.display = 'none';
        }
    } else {
        modal.classList.add('show');
        modal.style.display = 'block';
        if (backdrop) {
            backdrop.classList.add('show');
            backdrop.style.display = 'block';
        }
    }
}

function neo_upgrade_progress_bar(percentage)
{
    $('#issabel_addons_progress').css('width',percentage+'%');
    $('#issabel_addons_progress').attr('aria-valuenow',percentage);
    $('#issabel_addons_progress_value').text(percentage+'%');
}

function mostrar_dialogo_progreso()
{
    issabelAddonsModal('show');
    dialogo_progreso_abierto = true;
}

function ocultar_dialogo_progreso()
{
    issabelAddonsModal('hide');
	neo_upgrade_progress_bar(0);
	dialogo_progreso_abierto = false;
}

function loadingAddons()
{
     var loadingHTML = '<div class="iss-addons__empty">'
		    +'<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'
		      +'</div>';
     $('#addonlist').empty().append(loadingHTML);
}

function do_checkStatus()
{
	$.post('index.php?menu=' + module_name + '&rawmode=yes', {
		menu:		module_name,
		rawmode:	'yes',
		action:		'checkStatus'
	},
	function (respuesta) {
	      if(respuesta["db_error"]){ // Error en la base de datos local
		  ocultar_dialogo_progreso();
		  mostrar_mensaje(respuesta["db_error"],'error');
		  do_clearYum();
		  transaction_in_progress = false;
		  checking_dependencies = false;
		  clearInterval(intervalCheckStatus);
	      }
	      else if(respuesta["status"] == "error"){ // Error al realizar yum, pueden ser errores de dependencias
		  var error = "";
		  for(key in respuesta["error_description"])
		      error += respuesta["error_description"][key]+"\n";
		  ocultar_dialogo_progreso();
		  mostrar_mensaje(error,'error');
		  do_clearYum();
		  transaction_in_progress = false;
		  checking_dependencies = false;
		  clearInterval(intervalCheckStatus);
	      }
	      else if(respuesta["status"] == "busy"){ // Transacción en progreso
		  if(!dialogo_progreso_abierto)
		      mostrar_dialogo_progreso();
		  if(!intervalCheckStatus)
		      intervalCheckStatus = setInterval("do_checkStatus()",1000);
		  if(respuesta["action"]){
		      if(respuesta["action"] == "Checking Dependencies")
			checking_dependencies = true;
		  }
		  $('#feedback').text(respuesta["info"]);
		  $('#issabel_addons_modal_title').text(respuesta["title"]);
		  neo_upgrade_progress_bar(respuesta["percentage"]);
		  transaction_in_progress = true;
	      }
	      else if(respuesta["status"] == "idle"){ // Sistema ocioso
		  do_deleteActionTmp();
		  ocultar_dialogo_progreso();
		  clearInterval(intervalCheckStatus);
		  $('#feedback').text('');
		  if(transaction_in_progress){
		      if(respuesta["warnmsg"]){
			  mostrar_mensaje(respuesta["warnmsg"],'warning');
			  checking_dependencies = false;
		      }
		      else if(respuesta["transaction_status"])
			  mostrar_mensaje(respuesta["transaction_status"],'success');
		      if(!checking_dependencies)
			  do_listarAddons(null);
		      transaction_in_progress = false;
		  }
		  if(checking_dependencies){
		      if(!transaction_cancelled)
			  do_iniciarCompra();
		      checking_dependencies = false;
		  }
		  estadoCliente.name_rpm = null;
		  transaction_cancelled = false;
	      }
	});
}

function do_clearYum()
{
      $.post('index.php?menu=' + module_name + '&rawmode=yes', {
	menu:		module_name,
	rawmode:	'yes',
	action:		'clearYum'
	},
	function (respuesta) {
	});
}

function do_deleteActionTmp()
{
      $.post('index.php?menu=' + module_name + '&rawmode=yes', {
	menu:		module_name,
	rawmode:	'yes',
	action:		'deleteActionTmp'
	},
	function (respuesta) {
	});
}

function cancelTransaction()
{
    $.post('index.php?menu=' + module_name + '&rawmode=yes', {
	menu:		module_name,
	rawmode:	'yes',
	action:		'cancelTransaction'
	},
	function (respuesta) {
	    if(respuesta["error"])
		mostrar_mensaje(respuesta["error"],'error');
	    else if(respuesta["db_error"])
		mostrar_mensaje(respuesta["db_error"],'error');
	    else
		transaction_cancelled = true;
	});
}

function do_checkDependencies(serverId)
{
      var link = $('#'+estadoCliente.name_rpm+'_link').val();
      link += refer;
      if(serverId != null)
	link += "&serverkey="+serverId;
      $('#'+estadoCliente.name_rpm+'_link').val(link);

      if($('#'+estadoCliente.name_rpm+'_installed').val() == "yes")
	do_iniciarCompra();
      else{
	  $.post('index.php?menu=' + module_name + '&rawmode=yes', {
		    menu:		module_name,
		    rawmode:	'yes',
		    action:		'checkDependencies',
		    name_rpm:	estadoCliente.name_rpm
	    },
	    function (respuesta) {
		    $('body').css('cursor','default');
		    if(respuesta["db_error"])
			mostrar_mensaje(respuesta["db_error"],'error');
		    else if(respuesta["error"]){
			mostrar_mensaje(respuesta["error"],'error');
			do_checkStatus();
		    }
		    else if(!respuesta || respuesta["status"] === undefined){
		        /* La respuesta no es la que se espera: el servidor no ha podido
		         * hablar con el demonio actualizador. Mejor decirlo que dejar el
		         * modal de progreso congelado en 0%. */
		        mostrar_mensaje(issabel_addons_titulos.service_down,'error');
		    }
		    else{
			transaction_in_progress = true;
			checking_dependencies = true;
			mostrar_dialogo_progreso();
			$("#issabel_addons_modal_title").text(respuesta["title"]+" "+estadoCliente.name_rpm);
			intervalCheckStatus = setInterval("do_checkStatus()",1000);
		    }
	    });
      }
}
