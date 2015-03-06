// Run javascript after DOM is initialized
$(document).ready(function() {

  $('.collapse').on('show.bs.collapse', function () {
    $('.collapse.in').collapse('hide');
  });

  $('#search-universities').hideseek({ });

  $('#search-topics').hideseek({ });

});
