$(document).ready(function () {
    $('#transactionStats').tablesorter();

    updateTotalsFromTable();
});


function updateTotalsFromTable() {
    var num_sales = [];
    var sale_prices = [];
    var commissions = [];
    var totalNumSales = 0;
    var totalSales = 0;
    var totalCommission = 0;

    $('#transactions-form-data tr').each(function (idx, row) {
        if ($(row).is(':visible')) {
            var cells = $(row).children();
            num_sales.push($(cells[4]).html());
            sale_prices.push($(cells[3]).html());
            commissions.push($(cells[6]).html());
        }
    });

    for (var i = 0; i < num_sales.length; ++i) {
        var sale = parseFloat(sale_prices[i]);
        var num_sale = parseInt(num_sales[i], 10);
        totalCommission += parseFloat(commissions[i]);
        totalSales += sale * num_sale;
        totalNumSales += num_sale;
    }

    // shove results onto the page
    $('#total-num-sales').html(totalNumSales);
    $('#total-commission').html(totalCommission.toFixed(2));
    $('#total-sales').html(totalSales.toFixed(2));

}