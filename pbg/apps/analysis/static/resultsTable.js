// I hear you saying, "_wrapper? What's _wrapper? I don't see any
// _wrapper in the code." Basically, the dataTable class adds little
// doo-dads to each table, like pagination and a search bar, and puts
// all that information in an id that's the same as the underlying
// table's---plus a '_wrapper' suffix. Althougth hacky, including the
// wrapper in my id makes sure everything plays nicely with
// dataTables. -MM
$(function() {
	var activeNums;
	var getTabInfo = function($tab) {
		var id, match, name, num, $table;
		id = $tab.attr("id");
		match = /(\w+)_results_tab_(\d)/.exec(id);
		name = match[1];
		num = +match[2];
		$table = $("#" + name + "_results_table_" + num + "_wrapper");
		return {
			"name"   : name,
			"num"    : num,
			"$table" : $table
		};
	};

	activeNums = {};
	$('.results_tab').each(function() {
		var tabInfo, name, num, $table;
		tabInfo = getTabInfo($(this));
		name   = tabInfo["name"];
		num    = tabInfo["num"];
		$table = tabInfo["$table"];
		if (num === 1) {
			activeNums[name] = 1; // default tab is always tier 1
		} else {
			$table.hide();
		}
	});

	$('.results_tab').on({
		"click" : function() {
			var $activeTab, $activeTable, activeNum;
			var tabInfo, name, num, $table;
			tabInfo = getTabInfo($(this));
			name   = tabInfo["name"];
			num    = tabInfo["num"];
			$table = tabInfo["$table"];

			activeNum = activeNums[name];
			$activeTab = $("#" + name + "_results_tab_" + activeNum);
			$activeTable = $("#" + name + "_results_table_" + activeNum + "_wrapper");
			$activeTab.removeClass("active");
			$activeTable.hide();
			$(this).addClass("active");
			$table.show();
			activeNums[name] = num;
		}
	});
});
