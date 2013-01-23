(function( $ ){
  $.fn.address_book_import = function(options) {

    var yahoo_auth_url = "/contacts/yahoo/login/";
    var google_auth_url = "/contacts/authsub/login/";
    var signup_url = "/account/signup_connect_addr_friends/";

    var settings = {
      'get_data':function() { console.log('getting data'); },
      'loading_function':function() { },
    };


    if ( options ) { 
      $.extend( settings, options );
    }


    var loading_function = settings["loading_function"];
    var next_step = settings["next_step"];
    var run_import = settings["run_import"];

    var loaded_code = '';
// preload required html
    $.ajax({ async: false,  
             url: "/static/html/address_book_import.html #top_level", 
             success:function(data) { loaded_code = $(data); },
         });
           
    function load_remote(selector, callback) {
      return loaded_code.find(selector)
    }

    function load_remote_tmpl(selector, ds, callback) {
      var temp_tmpl = load_remote(selector, callback);
      var temp = $.tmpl(temp_tmpl, ds);
      return temp;
    }

    function redirect_to_next_step() {
      window.location.href = signup_url;
    }
    
    function build_address_overlay(abi_div) {
      if (settings["cancel"]) {
         var cancel = settings["cancel"];
      } else {
         var cancel = function() { abi_div.hide(); }        
      }

      abi_div.find('#close_address_book_import').click(function(event) { event.preventDefault(); cancel(); });
      abi_div.find('#skip_address_book_import').click(function(event) { event.preventDefault(); cancel(); });

      var import_from_isp = true;
  
      abi_div.find("#service").change(function(event) {    
         abi_div.find("#isp_login_form").each(function() { $(this).hide(); });
         var target_select = event.target;    
         var service = target_select.options[target_select.selectedIndex].value;
    
         if (service =='none') {
           abi_div.find("#isp_login_form").hide();       
         } else if (service =='generic') {
           abi_div.find("#isp_login_form").show();       
           abi_div.find("#isp_login_form_pwd").show();       
         } else {      
           abi_div.find("#isp_login_form").show();       
           abi_div.find("#isp_login_form_pwd").hide();              
         }  
      })


      abi_div.find("#invite_by_email").click(function(e) {
        e.preventDefault();
        abi_div.find("#import_div").hide();
        abi_div.find("#invite_box").show();    
        abi_div.find("#invite_by_email_p").hide();
        abi_div.find("#invite_from_address_p").show();
        import_from_isp = false;
      });


      abi_div.find("#invite_by_address").click(function(e) {
        e.preventDefault();
        abi_div.find("#import_div").show();
        abi_div.find("#invite_box").hide();    
        abi_div.find("#invite_by_email_p").show();
        abi_div.find("#invite_from_address_p").hide();
        import_from_isp = true;
      })

      function import_and_friend(type) {    
        abi_div.hide();
        run_import(type)
      }


      abi_div.find("#import_div_button").click(function(e) {
        e.preventDefault();
        abi_div.find("#import_div").find(".tips").remove();
        abi_div.find("#import_div").find(".error_tip").removeClass('error_tip');
    
        var ds = {} 
    
        if (import_from_isp) {
          var em_field = abi_div.find("#email");
          var em = em_field.val();
    
          var pw_field = abi_div.find("#password");
          var pw = pw_field.val();
    
          var service = abi_div.find("#service option:selected").val();
    
          if (! validate_email(em)) {
            set_wrong(em_field);
            create_tip(em_field, "Please enter a valid email",'left:80px; top: -20px;');
            return false;
          }

   
          if (service == 'gmail') {
            popup({ scrollbars: 1, center: 1, height: 435, width: 600, location: google_auth_url, onUnload: import_and_friend  });              
          } else if (service == 'yahoo') {
            popup({ scrollbars: 1, center: 1, height: 435, width: 600, location: yahoo_auth_url, onUnload: import_and_friend });            
          } else {
            if (! pw.length) {
              set_wrong(pw_field);        
              create_tip(pw_field, "Please enter a password",'left:80px; top: -20px;');
              return false;        
            }
    
            ds["service"]=service,
            ds["email"] = em;
            ds["password"] = pw;
    
            var animation_div = abi_div.find("#address_book_import").find(".importing");
            animation_div.show();
    
            response = ajax_call('/home/import_generic/',ds);
            animation_div.hide();
    
            if (response["success"]) {
              import_and_friend('isp')
            } else {
              create_tip(em_field, "Please enter a valid email and password",'left:80px; top: -20px;');
              return false;
            }
          }
    
        } else {
          ds["emails"] = abi_div.find("#email_list").val();
          response = ajax_call('/home/save_email_list/',ds);
          if (response["success"]) {
            import_and_friend('email_list');
          } else {
            if (! $("#invalid_email_addresses").length) {
              $("#invite_from_address_p").append("<br><span id='invalid_email_addresses' style='color:red;'>Invalid email addresses<br></span>")
            }
          } 
        }
      });
      return(abi_div);
    }

    var existing_div = false;
    if (settings["div"]) {
      var abi_div = settings["div"];
      existing_div = true;      
    } else { 
      var abi_div = load_remote('#address_book_import');
    }   

    var q = build_address_overlay(abi_div);
    if (! existing_div) {
      loading_function(true);
      q.hide();
      $("body").append(q);
  
      var lw = q.find(".lightbox_wrapper");
      lw.css('top',$(window).scrollTop() + 100);
  
      var maybe_new_height = $(window).scrollTop() + 100 + lw.outerHeight();
  
      var set_height = $(document).height();
      if (maybe_new_height > set_height) {
        set_height = maybe_new_height;
      }   
  
      q.height(set_height);
  
      q.fadeIn();
    }
};
})( jQuery );














(function( $ ){
  $.fn.email_invite_overlay = function(options) {

    var settings = {
      'get_data':function() { console.log('getting data'); },
      'loading_function':function() { }
    };


    if ( options ) { 
      $.extend( settings, options );
    }


    var loading_function = settings["loading_function"];
    var next_step = settings["next_step"];

    var loaded_code = '';
// preload required html
    $.ajax({ async: false,  
             url: "/static/html/address_book_import.html #top_level", 
             success:function(data) { loaded_code = $(data); },
         });
           
    function load_remote(selector, callback) {
      return loaded_code.find(selector)
    }

    function load_remote_tmpl(selector, ds, callback) {
      var temp_tmpl = load_remote(selector, callback);
      var temp = $.tmpl(temp_tmpl, ds);
      return temp;
    }

    function populate_email_invite_overlay(container_ul, non_users) {
      container_ul.empty();
  
      for (user_index in non_users) {
        var contact = load_remote_tmpl("#contact_list", non_users[user_index]);
        container_ul.append(contact)
      }
    }
  
    function show_only(abi_div, container_ul, start, limit) {
       container_ul.find("li").hide();
       var i = 0;
       var max = parseInt(start) + parseInt(limit);
       abi_div.find("#prev").hide();
       abi_div.find("#next").hide();


       container_ul.find("li").each(function(ele) {
         if ((i >= start ) && (i < max)) {
           $(this).show();
         }
         if (i >= max) {
           abi_div.find('#next').show();      
           return false;
         }
         i = i +1;              
       });    

       if (start > 1) {
         abi_div.find('#prev').show();      
       }

    }

    function build_invite_overlay(abi_div, response) {

      // abi_div.show();    
      //   
      var current_start_index = 0;
      var page_size = 8;

    
      if (response["success"]) {
        var non_users = response["non_users"];
        populate_email_invite_overlay(abi_div.find("#email_invite_list"), non_users);
        show_only(abi_div, abi_div.find("#email_invite_list"), current_start_index, page_size);
        var sort_keys = response["sort_keys"];
        if (sort_keys.length > 0) {
          for (skidx in sort_keys) {
            var sk_a = $('<a href="#" rel="' + sort_keys[skidx][1] + '">' + sort_keys[skidx][0] + '</a>');
            sk_a.click(function(e) {
                e.preventDefault();
                var index_loc = $(this).attr('rel');
                current_start_index = parseInt(index_loc);
                show_only(abi_div, abi_div.find("#email_invite_list"), current_start_index, page_size);
            });
            abi_div.find("#letter_navigation").append(sk_a);
          }
        }
      }

  
      abi_div.find("#next").click(function(e) {
        e.preventDefault();
        current_start_index = current_start_index+page_size;
        show_only(abi_div, abi_div.find("#email_invite_list"), current_start_index, page_size);                
      });
  
      abi_div.find("#prev").click(function(e) {
        e.preventDefault();
        current_start_index = current_start_index-page_size;
        show_only(abi_div, abi_div.find("#email_invite_list"), current_start_index, page_size);                
      });
  
      abi_div.find("#select_all").click(function(e) {
        e.preventDefault();
        abi_div.find("#email_invite_list").find('input[name=invite_id]').each(function (e) {
           $(this).attr('checked',true);
        });
      });
  
  
      abi_div.find("#select_none").click(function(e) {
        e.preventDefault();
        abi_div.find("#email_invite_list").find('input[name=invite_id]').each(function (e) {
           $(this).attr('checked',false);
        });
      });

      if (settings["cancel"]) {
         var cancel = settings["cancel"];
      } else {
         var cancel = function() { abi_div.hide(); }        
      }

      abi_div.find('#close_email_invite_overlay').click(function(event) { event.preventDefault(); cancel(); });
      abi_div.find('#skip_email_invite_overlay').click(function(event) { event.preventDefault(); cancel(); });
      var csrf_token = getCookie('csrftoken'); 
      abi_div.find('#email_invite_form').append($('<input type="hidden" name="csrfmiddlewaretoken" value="'+ csrf_token + '">'));

      return(abi_div);

    }


    var existing_div = false;
    if (settings["div"]) {
      var abi_div = settings["div"];
      existing_div = true;      
    } else { 
      var abi_div = load_remote('#email_invite_overlay');
    }   

    var import_now = false;
    if (settings["import_now"]) {
      import_now = true;
    }


    var ds = { };
    if (import_now) {
      ds["run_import"] = 1;        
    } 

    loading_function(false);

    ajax_async_call("/home/get_non_user_contacts/", ds, function(response) {
      var q = build_invite_overlay(abi_div, response);
      loading_function(true);
      if (! existing_div) {
        loading_function(true);
        q.hide();
        $("body").append(q);
    
        var lw = q.find(".lightbox_wrapper");
        lw.css('top',$(window).scrollTop() + 100);
    
        var maybe_new_height = $(window).scrollTop() + 100 + lw.outerHeight();
    
        var set_height = $(document).height();
        if (maybe_new_height > set_height) {
          set_height = maybe_new_height;
        }   
    
        q.height(set_height);
    
        q.fadeIn();
      }
    });


};
})( jQuery );
