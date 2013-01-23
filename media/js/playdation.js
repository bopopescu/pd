
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

$.ajaxSetup({
      beforeSend: function(xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
});



function ajax_call(url, ds) {
  var response = {};

  $.ajax({
    type: 'POST',
    traditional: true,
    url: url,
    data: ds,
    success: function(data) { response=data },
    dataType: 'json',
    async: false
  });
  return response;      
  
}

function ajax_async_call(url, ds, callback) {
  $.ajax({
    type: 'POST',
    traditional: true,
    url: url,
    data: ds,
    success: callback,
    dataType: 'json',
    async: true
  });
}










function accept_friendship(from_child, to_child, callback) {
  var ds = { "to_child": to_child, "from_child": from_child };

  response = ajax_call('/friends/confirm_friend/', ds);

  if (callback) {
    callback(response);
  }

  return response;      
}


function send_invitation(to_user, to_child, from_child, how_related, message) {
  var ds = { 
    "to_user": to_user, 
    "to_child": to_child, 
    "from_child": from_child,
    "message": message,
    "how_related": how_related, 
  };

  response = ajax_call('/friends/add_friend/', ds);

  return response;      
}

function send_invite(ds) {
  response = ajax_call('/friends/add_friend/', ds);

  return response;      
}


function send_message(to_user, subject, message) {
  var ds = { 
    "to_user": to_user, 
    "message": message,
    "subject": subject,
  };

  response = ajax_call('/messages/send_message/', ds);

  return response;
}



function validate_email(email) {
 var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,3})$/;
 return (reg.test(email));
}


function set_right(element) {
  element.removeClass("error_tip");
}

function set_wrong(element) {    
  element.addClass("error_tip");
}


var tip=$("<span class=\"tips\" style=\"left:100px;\"></span>");

function clone_tip(tip_contents) {
  var new_tip = tip.clone();
  new_tip.html("<b>"+tip_contents+"</b>");
  return new_tip;    
}

function create_tip(element, tip_contents, style) {
  var new_tip = clone_tip(tip_contents);
  if (style) {
    new_tip.attr('style',style);      
  }

  element.after(new_tip);
}


(function($) {
  var cache = [];
  // Arguments are image paths relative to the current page.
  $.preLoadImages = function() {
    var args_len = arguments.length;
    for (var i = args_len; i--;) {
      var cacheImage = document.createElement('img');
      cacheImage.src = arguments[i];
      cache.push(cacheImage);
    }
  }
})(jQuery)


Track = {
  init : function(identity, event_name) {
    this.identify(identity);
    this.record(event_name);  
  },

  identify : function(identifier) {
    _kmq.push(["identify", identifier]);
  },

  record : function(event_name, properties) {
    _kmq.push(["record", event_name, properties]);
  },

  track_click : function(event_name, dom_id, properties) {
    _kmq.push(["trackClick", dom_id, event_name, properties]);
  },

  track_click_by_class : function(event_name, dom_class, properties) {
    _kmq.push(["trackClick", "." + dom_class, event_name, properties]);
  }  
};


FBIntegration = {
  fb_loaded: function() {
    var rval = false;
    try {
      eval("FB");
      eval("FB.XFBML");
      rval = true;
    } catch(e) {
    }
    return rval;
  },

  fb_parse: function() {
    if (this.fb_loaded()) {
      FB.XFBML.parse();
    } else {
      try {
      } catch(e) {
      }
    }
  },

};


FacebookLogin = {
  processLogin: function(success_url, success_func, redirect_url, relogin) {
    var self = this;
    if (relogin == 'true') {
        FB.getLoginStatus(function(response) {
          if (response.session) {
            FB.logout(function(response) {FacebookLogin.processLogin(success_url, success_func, redirect_url, "false"); return false; });
          } else {
            FacebookLogin.processLogin(success_url, success_func, redirect_url, "false"); return false;
          }
        });

    } else {
        if (FBIntegration.fb_loaded()) {
          FB.login(
            function(response) {
              self.processResponse(response, success_url, success_func, redirect_url);
            }, {
            perms:'email,user_location'
          });
        } else {
          var response = new Object();
          response.perms = function() {
            return {};
          };
          response.session = function() {
            return {};
          };
          self.processResponse(response, success_url, success_func, redirect_url);
        }
    }
  },

  processResponse: function(response, success_url, success_func, redirect_url) {
    var self = this;
    if (response.session) {
      if (response.perms) {
        self.track_allow();
        if (success_func != null) {
          success_func(response, success_url, redirect_url);
        } else {
          top.location = success_url;
        }
      } else {
        self.track_dont_allow_perms();
        self.failed(response, redirect_url);
      }
    } else {
      self.track_dont_allow_session();
      self.failed(response, redirect_url);
    }
  },

  failed: function(response, redirect_url) {
    top.location = redirect_url;
  },

  track_allow : function() {
    Track.record("Allowed facebook");
  },

  track_dont_allow_session : function() {
    Track.record("Did not allow facebook - session");
  },

  track_dont_allow_perms : function() {
    Track.record("Did not allow facebook - perms");
  }
};

Message = {
  display : function(message) {
    var top_div = $('<div id="message_display" class="siteerror"><div class="innet-sitererror"><span><b>'+message+'</b></span></div></div>');
    $("body").prepend(top_div);
    var id = setTimeout(function() { $("#message_display").slideUp();  }, 3000)
  },
}

// onmouseover="Tooltip.show($(this), 'Header', 'Message'); return false;" onmouseout='$(".tooltip").hide;'
Tooltip = {
  show : function(element, header, message) {
    var position = $(element).offset()
    var left = position.left;
    var top = position.top;
    var tooltip_id = 'tooltip_' + new Date().getTime();
    var tooltip = $('<div id="'+tooltip_id+'" class="tooltip" style="position:absolute; display:none; left:'+left+'px; top:'+top+'px; z-index:9999;"><span class="arrow"><img src="/static/images/bg_arrow_right.png" alt="" width="6" height="11" /></span><a href="#" class="close_btn tooltip_close_btn" style="left:10px;">X</a> <div class="blue_box"> <h3>'+header+'</h3><p>'+message+'</p></div></div>');
    tooltip.find(".tooltip_close_btn").click(function(e) { e.preventDefault; $("#"+tooltip_id).fadeOut(); })
    $("body").append(tooltip);
    tooltip.fadeIn();
    var id = setTimeout(function() { $("#"+tooltip_id).fadeOut();  }, 8000)
    return tooltip_id;
  },
  hide: function(element_id) {
    $("#"+element_id).fadeOut();    
  }
}
