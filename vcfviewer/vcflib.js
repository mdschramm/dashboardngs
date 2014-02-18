
	//
	// VCF visualization, filtering and some simple statistics library
	// relies on jQuery and d3
	// written and maintained by Yevgeniy Antipin at Icahn School of Medicine at Mount Sinai, 2013
	//

	var nl = "\n", tab = "\t";
	function isset(a) { return typeof a!=='undefined'; }	// yay php
	// $.browser.chrome = /chrome/.test(navigator.userAgent.toLowerCase());

	function getBioLink(type, id, text) {
		switch(type) {
		case 'genename': return "<a href='http://www.ncbi.nlm.nih.gov/gene/?term=" + id + "'+human' target='_blank'>" + text + "</a>"; break;
		case 'uniprot':  return "<a href='http://www.uniprot.org/uniprot/" + id + "' target='_blank'>" + text + "</a>"; break;
		case 'pfam':     return "<a href='http://pfam.sanger.ac.uk/protein/" + id + "' target='_blank'>" + text + "</a>"; break;
		case 'omim':     return "<a href='http://www.omim.org/entry/" + id + "' target='_blank'>" + text + "</a>"; break;
		case 'enst':     return "<a href='http://useast.ensembl.org/Homo_sapiens/Transcript/Summary?t=" + id + "' target='_blank'>" + text + "</a>"; break;
		default: return '';
		}
	}

	function fillinc(ary, len) { for(var p=0; p<len; p++) ary.push(p); } // make sure ary is an empty array before calling
	function getBox(w, h, margin) { return { l:margin, t:margin, r:w-margin, b:h-margin, w:w-2*margin, h:h-2*margin } }
	function getRange(from, to, steps) { return { from:from, to:to, steps:steps, w:to-from }; }
	function getRangeUpdate() { return {
		min:1e+6, max:-1e+6, width:0,
		update: function(v) { if (v>this.max) this.max = v; if (v<this.min) this.min = v; this.width = this.max-this.min; }}}

	// sort by values and maintain indices in parallel order, not too efficient though
	function sort(values, indices) {
		if (values.length!=indices.length) return false;
		var l = [];
		for(var k=0; k<values.length; k++) l.push({ v:values[k], i:indices[k] });
		l.sort(function(a,b){ return b.v-a.v });
		values = []; indices = [];
		for(var k=0; k<l.length; k++) { values.push(l.v[k]); indices.push(l.i[k]) };
		return true;
	}

	// ---------------------------------- VCF table reader with filtering and nice html table rendering ----------

	function createVCF() {
	return {
		asyncTimeout : 2,
		cb	: false,		// callback obj
		order : [],
		data : [],
		htable : '',		// html
		seqlimit : 12,
		passonlyQ : false,	// skip non-PASS lines to reduce size
		column : { chr:0, pos:1, id:2, ref:3, alt:4, qual:5, filter:6, info:7, format:8, normal:9, tumor:10 },
		fields : { 'SNPEFF_GENE_NAME':'genename', 'SNPEFF_TRANSCRIPT_ID':'enst', 'OMIM_GENE':'omim', 'OMIM_PHENO':'omim' },
		filter : { Somatic:true, LOH:false, Germline:false, Unknown:false, other:false },
		vartypeCount : { Somatic:0, LOH:0, Germline:0, Unknown:0, other:0, read:0, skipped:0 },
		emptyColumns : {},	// some columns are empty or have only one value, no point showing them

		// TODO: paging not implemented yet
		// paging: current page of visible rows
		// from = idx * len;
		page : { from:0, idx:0, len:1000 },

		info2obj : function(str) {
			var o = {}, w = str.split(';');
			for(var v in w) {
				var ww = w[v].split('=');
				var key = ww[0], val = ww.length>1 ? ww[1] : false;
				o[key] = val;
			}
			return o;
		},

		// starts reading/parsing 'text' asynchronously
		// cb   -- callback object, must have 3 functions: { progress(), done(), fail() }
		// filter -- filter object: { Somatic:true, LOH:false, Germline:false, Unknown:false, other:false }
		//
		asyncReadFromText : function(text, filter, cb) {
			if (cb) this.cb = cb;
			this.filter = filter;
			this.readyQ = false;
			this.order = [];
			this.info = { keys:{}, names:[] };
			vartypeCount = { Somatic:0, LOH:0, Germline:0, Unknown:0, other:0, read:0, skipped:0 };
			this.asyncParseLineN = 0;
			this.asyncParseStop = 1000;
			this.fileLines = text.split(nl);
			console.log('reading VCF ' + this.fileLines.length + ' lines total');
			if (!this.fileLines.length) { if (this.cb) this.cb.done(); return; }
			if (this.cb) this.cb.progress('reading VCF...');
			setTimeout($.proxy(this.asyncParse, this), this.asyncTimeout);
		},
		asyncParse : function() {

			for (var currN=0; this.asyncParseLineN<this.fileLines.length
						&& currN<this.asyncParseStop; this.asyncParseLineN++, currN++) {
				var i = this.asyncParseLineN;
				var line = this.fileLines[i];
				if (line.length<2) continue;
				var ch = line.charAt(0);
				if (ch=='#' && line.charAt(1)=='#') continue;
				if (ch=='#') { this.colnames = line.substr(1).split(tab); continue; }
				var w = line.split(tab);
				if (w.length<11) {
					if (this.cb) this.cb.fail('at least 11 columns expected in VCF file, less found at line #' + i);
					return false;
				}
				if (this.passonlyQ && w[this.column.filter]!='PASS') { this.vartypeCount.skipped++; continue; }
				this.vartypeCount.read++;
				var obj = this.info2obj(w[this.column.info]);
				for(var key in obj) {
					var val = obj[key];
					if (!this.info.keys.hasOwnProperty(key)) { this.info.keys[key] = this.info.names.length; this.info.names.push(key); }
					if (key=='VS_SS') {
						if (this.vartypeCount.hasOwnProperty(val)) this.vartypeCount[val]++;
						else this.vartypeCount.other++;
					}
				}
				w[this.column.info] = obj;	// replace string with parsed obj
				this.data.push(w);
			}
			if (this.cb) this.cb.progress('reading VCF, line ' + (i+1));
			if (this.asyncParseLineN<this.fileLines.length) { setTimeout($.proxy(this.asyncParse, this), this.asyncTimeout); return; }
			console.log('left ' + this.data.length + ' rows total');
			this.asyncParseLineN = this.asyncCurrRow = 0;
			setTimeout($.proxy(this.reRender, this), this.asyncTimeout);
		},
		
		// compute selection based on current filtering and call asyncRender();
		reRender : function(filter) {
			if (isset(filter)) this.filter = filter;
			this.htable = '<table cellspacing=1 class="vcf"><tr>';
			for(var i in this.colnames) {
				if (this.column.info==i) {
					for(var j in this.info.names) this.htable += '<td class="thdr">' + this.info.names[j] + '</td>';
					continue;
				}
				this.htable += '<td class="thdr">' + this.colnames[i] + '</td>';
			}
			this.htable += '</tr>' + nl;
		//	console.log('LOH = ' + this.filter.LOH);
			this.order = [];
			for(var i in this.data) {
				if (!this.data[i][this.column.info].hasOwnProperty('VS_SS')) continue;
				var vartype = this.data[i][this.column.info]['VS_SS'];
				if (this.filter.hasOwnProperty(vartype) && this.filter[vartype]) {
					this.order.push(i);
				}
			}
			this.asyncCurrRow = 0;
			setTimeout($.proxy(this.asyncRender, this), this.asyncTimeout);
		},

		//
		// --- rendering html table -------------------------------------------------------------------------------------------
		//
		asyncRender : function() {

			for (var currN=0; this.asyncCurrRow<this.order.length && currN<this.asyncParseStop; this.asyncCurrRow++, currN++) {
				var i = this.order[this.asyncCurrRow];
				var cla = currN%2 ? 'tbgr1' : 'tbgr2';
				var htmlrow = '<tr class="' + cla + '">';
				for(var c in this.data[i]) {
					if (c==this.column.info) {
						var obj = this.data[i][c];
						for(var idx in this.info.names) {
							var name = this.info.names[idx];
							var link = this.fields.hasOwnProperty(name) ? getBioLink(this.fields[name], obj[name], obj[name]) : obj[name];
							if (obj.hasOwnProperty(name) && obj[name]!==false) htmlrow += '<td>' + link + '</td>';
							else htmlrow += '<td> </td>';
						}
						continue;
					}
					if (c==this.column.ref || c==this.column.alt) {
						htmlrow += '<td>'
							+ (this.data[i][c].length>this.seqlimit ? this.data[i][c].substr(0, this.seqlimit) + '..' : this.data[i][c])
							+ '</td>';
					} else htmlrow += '<td>' + this.data[i][c] + '</td>';
				}
				this.htable += htmlrow + '</tr>' + nl;
			}
			var prc = Math.floor(100*this.asyncCurrRow/this.order.length);
			if (this.cb) this.cb.progress('rendering table .. ' + prc + '%');
			if (this.asyncCurrRow<this.order.length) { setTimeout($.proxy(this.asyncRender, this), this.asyncTimeout); return; }
			if (this.cb) {
				this.htable += '</table>' + nl;
				this.cb.progress('updating html...');
				// let progress window update, otherwise it's stuck at ugly 98% for couple of secs
				setTimeout($.proxy(this.cb.doneReading, this), this.asyncTimeout);
			}
		}
	}};
	
	
	
	
	
	
	
	
	
	
	
	