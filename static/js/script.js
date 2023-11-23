/* jshint esversion: 11 */
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
  let modal = document.querySelectorAll('.modal');
  M.Modal.init(modal, {
    dismissable: false
  });
  let autocomplete = document.querySelectorAll('.autocomplete');
  M.Autocomplete.init(autocomplete, {
    minLength: 0,
    data: [
      { id: "Mrs" },
      { id: "Mr" },
      { id: "Miss" },
      { id: "Ms" },
      { id: "Mx" },
      { id: "Dr" },
    ]
  });
});