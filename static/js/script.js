  document.addEventListener('DOMContentLoaded', function () {
    let sidenav = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenav, { edge: "right" });
    let collapsible = document.querySelectorAll('.collapsible');
    M.Collapsible.init(collapsible);
    let select = document.querySelectorAll('select');
    M.FormSelect.init(select);
    let datepicker = document.querySelectorAll('.datepicker');
    M.Datepicker.init(datepicker, {
      format: "dd mmmm, yyyy",
     yearRange: 0,
     autoClose: true,
    });
  });