/**
 * Created by serega on 05.12.17.
 */
$(function () {
  /* 1. OPEN THE FILE EXPLORER WINDOW */
  $(".js-upload-photos").click(function () {
    $("#fileupload").click();
  });

  /* 2. INITIALIZE THE FILE UPLOAD COMPONENT */
  $("#fileupload").fileupload({
    url: '/exp/',
    done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
      if (data.result.is_valid) {

        $("#id_doc").prepend("<option value=" + data.result.id + "\"" + " selected=\"" + data.result.id + "\">" + data.result.name + "</option>"
        )
      }
    }
  });

});