$(function() {
    var availableGenes = Object.keys(geneMap);
    $("#id_gene").autocomplete({
        source: function(request, response) {
                    var results = $.ui.autocomplete.filter(availableGenes, request.term);
                    response(results.slice(0,10));
                },
        select: function(event, ui) {
                    $("#id_gene").val(ui.item.value);
                    $('select[name=chromosome]').val((geneMap[$("#id_gene").val()][0]).slice(3));
                    $('input[name=start]').val(geneMap[$("#id_gene").val()][1]);
                    $('input[name=stop]').val(geneMap[$("#id_gene").val()][2]);
                },
        open: function(event, ui) {
                      if(geneMap[$("#id_gene").val().toUpperCase()] != undefined) {
                        $('select[name=chromosome]').val((geneMap[$("#id_gene").val()][0]).slice(3));
                        $('input[name=start]').val(geneMap[$("#id_gene").val()][1]);
                        $('input[name=stop]').val(geneMap[$("#id_gene").val()][2]);
                      }
              }         
    });
});


$("#id_gene, input[name=chromosome], input[name=start], input[name=stop]").keydown(function (e) {
    if(e.keyCode == 13) {
        $("#submit").trigger("click");
    }
});


// This file takes care of autocompletion, populating the form fields based on gene name, and submitting the form when the enter key is pressed.