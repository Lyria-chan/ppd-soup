function removeFromDict(dict,keys)
{
	for (key of keys)
	{
		delete dict[key]
	}
	return dict
}

//================================================

function sortByKey(array, key) 
{
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key]
        return ((x < y) ? -1 : ((x > y) ? 1 : 0))
    })
}

//================================================

function zfill(num, len) 
{
    if (String(num).length < len)
    {
        return (Array(len).join("0") + num).slice(-len)
    }
    else
    {
        return String(num)
    }
}

//================================================

function convertDuration(d)
{
    let hr
    let min
    if (d >= 3600)
    {
        hr = String(Math.floor(d/3600)) + ':'
        d = d%3600
        min = zfill(Math.floor(d/60),2)
    }
    else
    {
        hr = ''
        min = Math.floor(d/60)
    }
    d = hr + min + ':' + zfill(d%60,2)
    return d
}

//================================================//
// "More" tab
//================================================//

function displayMore(no)
{
	//----------------------------------------------
	// Generates and displays the "More" tab
	// using data from freshly parsed JSON.
	// "no" var from "levellistId" in song dict
	//----------------------------------------------
	
	more.classList.toggle('hideTransition')
	let ll = JSON.parse(levellist)
	let data = ''
	data += '<div><div>Title: <a href="https://projectdxxx.me/score/index/id/' + ll[no]['more']['id'] + '">' + ll[no]['title'][1] + '</a>'
	if (ll[no]['title'][0] != ll[no]['title'][1])
	{
		data += '<br>Title (converted): ' + ll[no]['title'][0]
	}
	data += '<br>Author: ' + ll[no]['author'][1]
	if (ll[no]['author'][0] != ll[no]['author'][1])
	{
		data += '<br>Author (converted): ' + ll[no]['author'][0]
	}
	data += '<br>Author ID: <a href="https://projectdxxx.me/user/index/id/' + ll[no]['more']['authorId'] + '"><img src="https://projectdxxx.me/api/get-avator/s/16/id/' + ll[no]['more']['authorId'] + '"> ' + ll[no]['more']['authorId'] + '</a>'
	data += '<br>Upload date: ' + new Date(ll[no]['date']*1000).toLocaleDateString()
	data += '<br>CSInput: '
	if (ll[no]['csinput']) {data += '✔️'}
	else {data += '❌'}
	data += '<br>Downloads: ' + ll[no]['downloads']
	data += '<br>Rating: '
	if (ll[no]['more']['voted'] == 0) {data += '-'}
	else
	{
		data += ll[no]['rating'].toFixed(2)
	}
	data += '<br>Votes: '
	if (ll[no]['more']['voted'] == 0) {data += '-'}
	else
	{
		data += ll[no]['more']['voted']
	}
	//data += '<br>Duration: ' + new Date(ll[no]['duration']*1000).toISOString().substring(14, 19)
    data += '<br>Duration: ' + convertDuration(ll[no]['duration'])
	data += '<br>BPM: ' + ll[no]['more']['bpm']
	
	
	
	// OLD METHOD - soup getText from unicode to html
	/*let desc = ll[no]['more']['desc'].replaceAll('\n','<br>').replaceAll('[Lock]','')
	let ytId = desc.match(/\[youtube id:(.*)\]/i)
	
	if (ytId)
	{
		ytId = ytId[0].replace('[youtube id:','').replace(/\s(.*)\]/i,'').replace(']','')
		desc = desc.replace(/\[youtube id:(.*)\]/i,'')
		data += '<br><a href="https://youtu.be/' + ytId + '">YouTube video</a>'
	}
	data += '</div><div><p class="levelDesc">' + desc + '</p></div>'*/
	
	// NEW BUT NOT WORKING METHOD - will work with raw html from soup
	/*data += '</div>' + ll[no]['more']['desc'].replace(' class="clearfix"','')
    document.querySelector('#infopanel > div').innerHTML = data
	// still uses unicode instead of html tags???
	// ?   ?   ?
	*/
	
	// TEMPORARY METHOD - 'raw' but not raw html changed from unicode
	let desc = ll[no]['more']['desc'].replace('\n','').replaceAll('\n','<br>').replaceAll('[Lock]','')
	let ytId = desc.match(/\[youtube id:(.*)\]/i)
	
	if (ytId)
	{
		ytId = ytId[0].replace('[youtube id:','').replace(/\s(.*)\]/i,'').replace(']','')
		desc = desc.replace(/\[youtube id:(.*)\]/i,'')
		data += '<br><a href="https://youtu.be/' + ytId + '">YouTube video</a>'
	}
	
    //diff tab
	data += '</div><div>Difficulty:'
	for (let diff of ['Easy','Normal','Hard','Extreme'])
	{
        //if diff exists
		if (ll[no]['difficulty']['p' + diff] != 0)
		{
			data += '<br>' + diff + ' - '
            //if stars exist
			if (ll[no]['difficulty']['s' + diff] != '')
			{
                if (!ll[no]['difficulty']['a' + diff])
                {
				    data += '<span>☆' + ll[no]['difficulty']['s' + diff] + '</span> (' + ll[no]['difficulty']['p' + diff] + ' pt)'
                }
                //if stars are approximated
                else
                {
                    data += '<span class="approx">☆' + ll[no]['difficulty']['s' + diff] + '</span> (' + ll[no]['difficulty']['p' + diff] + ' pt)'
                }
			}
			else
			{
				data += ll[no]['difficulty']['p' + diff] + ' pt'
			}
		}
	}
	data += '</div></div>'
	data += desc
    document.querySelector('#infopanel > div').innerHTML = data
	
	// cleaning up the desc div
	document.querySelector('#infopanel > div > div:nth-of-type(2)').removeAttribute('style')
	document.querySelector('#infopanel > div > div:nth-of-type(2)').removeAttribute('class')
	document.querySelector('#infopanel > div > div:nth-of-type(2)').nextSibling.remove()
	
	// removing <br> as long as they are at the end of desc
	let br = document.querySelector('#infopanel > div > div:nth-of-type(2)').lastChild
	while (br.tagName == 'BR')
	{
		br.remove()
		br = document.querySelector('#infopanel > div > div:nth-of-type(2)').lastChild
	}
}

//================================================

function hideMore()
{
	//----------------------------------------------
	// Hides the "More" tab 
	// and erases all data from #more tag
	//----------------------------------------------
	
	if (more != event.target) 
	{
		return
	}
	more.classList.toggle('hideTransition')
	let data = document.querySelector('#infopanel > div')
	data.innerHTML = ''
}

//================================================//
// Main song browser and table generator modules
//================================================//

function downloadLevels(maxpg = 0)
{
	//----------------------------------------------
	// Initiates loading animation,
	// calls python handle() function.
	// Result is converted to nice JSON with dicts
	// by convertLl() function
	// and then passed to displayTable() function
	//----------------------------------------------
	
	loading.classList.toggle('hideTransition')
    searchMode = document.querySelector('#searchbox > select').value
    levellist = eel.importPPD(kw.value,mode=searchMode,maxpages=maxpg)()
	//levellist = eel.importPPD(kw.value)()
	levellist.then((result) => 
	{
		levellist = result
		loading.classList.toggle('hideTransition')
		console.log('levellist downloaded')

		levellist = convertLl(levellist)
		displayTable(levellist)
	})
}

//================================================

function convertLl(ll)
{
	//----------------------------------------------
	// Converts python-formatted data
	// into more display-friendly format
	// and then returns the list as a JSON string
	//----------------------------------------------
	
	let levellistId = 0
	for (let l of ll)
	{
		l['levellistId'] = levellistId
		l['title'] = [l['title'],l['jpTitle']]
		l['author'] = [l['author'],l['jpAuthor']]
		
		l['downloads'] = Number(l['downloads'])
		l['rating'] = Number(l['rating'])
	
		l['more'] = {
			'id':l['id'],
			'bpm':Number(l['bpm']),
			'voted':Number(l['voted']),
			'desc':l['desc'],
			'authorId':l['authorID'],
			'video':l['dlLink']
		}
        
        for (diff of ['Easy','Normal','Hard','Extreme'])
        {
            if (l['s' + diff] > 1000)
            {
                l['s' + diff] -= 1000
                l['a' + diff] = true
            }
            else
            {
                l['a' + diff] = false
            }
        }
		
		l['difficulty'] = {
			'pEasy':Number(l["pEasy"]),
			'pNormal':Number(l["pNormal"]),
			'pHard':Number(l["pHard"]),
			'pExtreme':Number(l["pExtreme"]),
			'sEasy':l['sEasy'],
			'sNormal':l['sNormal'],
			'sHard':l['sHard'],
			'sExtreme':l['sExtreme'],
			'aEasy':l['aEasy'],
			'aNormal':l['aNormal'],
			'aHard':l['aHard'],
			'aExtreme':l['aExtreme']
		}
		
		let duration = l['duration']
		duration = duration.split(':')
		duration = Number(duration[0] * 60) + Number(duration[1])
		l['duration'] = duration
		
		
		l = removeFromDict(l,['jpTitle','jpAuthor','id','bpm','voted','desc','pEasy','pNormal','pHard','pExtreme','sEasy','sNormal','sHard','sExtreme','dlLink','authorID'])
		
		levellistId += 1
	}
    ll = JSON.stringify(ll)
	
	return ll
}

//================================================

function applyDisplayOptions()
{
	//----------------------------------------------
	// Gets display parameters from the user
	// and applies them by displayTable() function
	//----------------------------------------------
	
	//let param1 = document.querySelector('#options_set > select').value
	
	//let param2
	
	//if (sortDirDesc.checked) {param2 = true}
	//else {param2 = false}
    
    let param1 = sorting.sortBy
    let param2 = sorting.sortDesc
	
	let param3 = 15
	let param4 = convertToRomaji.checked
	let param5 = displayLessDiff.checked
	
	displayTable(levellist, sortBy = param1, sortDesc = param2, maxrows = param3, romaji = param4, less = param5)
}

//================================================

function displayTable(ll, sortBy = 'date', sortDesc = true, maxrows = 15, romaji = true, less = true, filterBy = false)
{
	//----------------------------------------------
	// Loads and applies sorting, filtering
	// and displaying options
	// (temp: cuts to maxrows number of songs)
	// and passes the formatted for display list
	// to generateTable() function
	//----------------------------------------------
	
    ll = JSON.parse(ll)
    
	displayFilters()
	ll = filter(ll)
	
	ll = sortByKey(ll,'date')
	ll = sortByKey(ll,sortBy)
	if (sortDesc) {ll.reverse()}
	
	romaji = !romaji
	ll = ll.slice(0,maxrows)
	
	let no = 1
	for (l of ll)
	{
		l['title'] = l['title'][Number(romaji)]
		l['author'] = l['author'][Number(romaji)]
		
		l['date'] = new Date(l['date']*1000).toLocaleDateString()
		l['duration'] = convertDuration(l['duration'])
		
		if (l['csinput']) {l['csinput'] = '✔️'}
		else {l['csinput'] = '❌'}
		
		if (l['more']['voted'] == 0) {l['rating'] = '-'}
		
		if (!isNaN(l['rating'])) 
		{
			//l['rating'] = Number(l['rating']).toFixed(2)
			l['rating'] += ' (' + l['more']['voted'] + ')'
		}
		
		l['no'] = no
		no += 1
	}
    
	generateTable(ll,lessDiff=less)
}

//================================================

function generateTable(ll, lessDiff)
{
	//----------------------------------------------
	// Does all the HTML work with
	// generating a table from the prepared list
	//----------------------------------------------
	
    if (document.contains(document.querySelector('#resultstab')))
    {
        resultstab.remove()
    }

    //let original_keys = ["id", "jpTitle", "title", "jpAuthor", "author", "csinput", "date", "downloads", "bpm", "rating", "voted", "duration", "pEasy", "pNormal", "pHard", "pExtreme", "sEasy", "sNormal", "sHard", "sExtreme", "desc"]
	
	let keys = ['no','title', 'author', 'date', 'csinput', 'downloads', 'rating', 'duration', 'sEasy', 'sNormal', 'sHard', 'sExtreme', 'i']
    //additional hidden key 'more'
	
	let dkeys = ['No.','Title', 'Author', 'Upload date', 'CSInput', 'Downloads', 'Rating', 'Duration', 'Difficulty', 'More']
	
    let table = document.createElement('table')
    let tbody = document.createElement('tbody')
    let row = document.createElement('tr')
    for (let n = 0; n < dkeys.length; n += 1)
    {
        let cell = document.createElement('th')
        /*
        if (['No.','More'].includes(key))
        {
            cell.innerText = key
        }
        else
        {
            cell.innerHTML = '<span class="sorting">' + key + '</span>'
        }*/
        
        if (!['No.','More'].includes(dkeys[n]))
        {
            cell.classList.add('sorting')
            if (dkeys[n] == 'Difficulty')
            {
                cell.setAttribute('onclick','setSorting("sExtreme")')
            }
            else if (dkeys[n] != 'More')
            {
                cell.setAttribute('onclick','setSorting("' + keys[n] + '")')
            }
        }
        cell.innerText = dkeys[n]
        
        if (dkeys[n] == 'Difficulty')
        {
            if (!lessDiff)
            {
                cell.setAttribute('colspan','4')
                cell.innerHTML = 'Difficulty<br><span>Easy | Normal | Hard | EX</span>'
            }
            else
            {
                cell.setAttribute('colspan','2')
                cell.innerHTML = 'Difficulty<br><span>Hard | EX</span>'
            }
        }
        row.appendChild(cell)
    }
    tbody.appendChild(row)

	let levelno = 0
    for (let level of ll)
    {
        let row = document.createElement('tr')
        for (let key of keys)
        {
            let cell = document.createElement('td')
            
            if (key == 'title')
            {
                let a = document.createElement('a')
                a.setAttribute('href','https://projectdxxx.me/score/index/id/' + level['more']['id'])
                a.innerText = level[key]
                cell.appendChild(a)
            }
            else if (key == 'author')
            {
                let a = document.createElement('a')
                //a.setAttribute('href','#')
                a.setAttribute('href','https://projectdxxx.me/user/index/id/' + level['more']['authorId'])
                a.innerText = level[key]
                cell.appendChild(a)
            }
            else if (['sEasy', 'sNormal', 'sHard', 'sExtreme'].includes(key))
            {
                if (['sEasy', 'sNormal'].includes(key)&&lessDiff)
                {
                    continue
                }
                if (level['difficulty'][key])
                {
                    cell.innerText = '☆' + level['difficulty'][key]
                }
                
                
                //if stars exist
                if (level['difficulty'][key] != '')
                {
                    let diff = key.slice(1)
                    if (!level['difficulty']['a' + diff])
                    {
                        cell.innerHTML = '<span>☆' + level['difficulty']['s' + diff] + '</span>'
                    }
                    //if stars are approximated
                    else
                    {
                        cell.innerHTML = '<span class="approx">☆' + level['difficulty']['s' + diff] + '</span>'
                    }
                }
                else
                {
                    cell.innerHTML = ''
                }
                cell.setAttribute('class','diff')
            }
			else if (key == 'i')
			{
				cell.innerText = 'ℹ️'
				cell.setAttribute('levelno',levelno)
				cell.setAttribute('levellistId',level['levellistId'])
			}
            else
            {
                cell.innerText = level[key]
            }
            
            if (!['title','author'].includes(key))
            {
                cell.style.textAlign = 'center'
            }
            row.appendChild(cell)
        }
        tbody.appendChild(row)
		levelno += 1
    }
    table.setAttribute('class','table table-striped')
    table.appendChild(tbody)
    table.setAttribute('id','resultstab')
    tabpanel.appendChild(table)
	
	let infocells = document.querySelectorAll('.table-striped tr:not(:first-child) td:last-child')
	for (cell of infocells)
	{
		cell.setAttribute('onclick','displayMore(' + cell.getAttribute('levellistId') + ')')
	}
    
    let th
    keys.forEach(function(key,no)
    {
        //document.querySelector('th:nth-of-type(' + (no + 1) + ')').setAttribute('class','sorting')
        if (key == sorting.sortBy)
        {
            th = document.querySelector('th:nth-of-type(' + (no + 1) + ')')
        }
    })
    
    if (sorting.sortDesc)
    {
        th.classList.add('desc')
    }
    else
    {
        th.classList.add('asc')
    }
}

//================================================//
// Filtering modules
//================================================//

function clearFilters()
{
	//----------------------------------------------
	// Just clears the filters, both in HTML and JS
	//----------------------------------------------
	
	filters = []
	filterList.innerHTML = ''
}

//================================================

function addFilter()
{
	//----------------------------------------------
	// Adds a new, empty filter to the list
	// and displays the whole filter list
	//----------------------------------------------
	
	filters.push(
	{
		'key':'title',
		'opt':false,
		'value':''
	})
	displayFilters()
}

//================================================

function loadFilters()
{
	//----------------------------------------------
	// Loads filters from the interface to the list
	//----------------------------------------------
	
	let newFilters = document.querySelectorAll('#filterList > li')
	for (let i=0; i < newFilters.length; i += 1)
	{
		if (['date','duration'].includes(filters[i]['key']))
		{
			filters[i]['opt'] = newFilters[i].querySelector('select:nth-of-type(2)').value
			filters[i]['value'] = newFilters[i].querySelector('input').value
		}
		else if (filters[i]['key'] == 'csinput')
		{
			filters[i]['value'] = newFilters[i].querySelector('select:nth-of-type(2)').value
		}
		else
		{
			filters[i]['opt'] = false
			filters[i]['value'] = newFilters[i].querySelector('input').value
		}
		
		filters[i]['key'] = newFilters[i].querySelector('select').value
	}
}

//================================================

function displayFilters()
{
	//----------------------------------------------
	// Displays the filters loaded from the list
	// AFTER loading them from the interface
	//----------------------------------------------
	
	loadFilters()
	filterList.innerHTML = ''
	for (let i=0; i < filters.length; i += 1)
	{
		let li = document.createElement('li')
		li.innerHTML = "<label>Filter by&nbsp</label><select><option value='title'>title</option><option value='author'>author</option><option value='authorId'>author ID</option><option value='date'>upload date</option><option value='csinput'>CSInput</option><option value='duration'>duration</option></select>&nbsp"
		if (filters[i]['key'] == 'date')
		{
			li.innerHTML += "<select><option value='before'>before</option><option value='after'>after</option></select><label>&nbsp</label><input type='date' class='filterValue'>"
			if (!['before','after'].includes(filters[i]['opt']))
			{
				filters[i]['opt'] = 'before'
			}
			li.querySelector('select:nth-of-type(2)').value = filters[i]['opt']
			
		}
		else if (filters[i]['key'] == 'duration')
		{
			li.innerHTML += "<select><option value='above'>above</option><option value='below'>below</option></select><label>&nbsp</label><input type='number' min=0 max=9999 class='filterValue'>"
			if (!['above','below'].includes(filters[i]['opt']))
			{
				filters[i]['opt'] = 'above'
			}
			li.querySelector('select:nth-of-type(2)').value = filters[i]['opt']
		}
		else if (filters[i]['key'] == 'csinput')
		{
			li.innerHTML += "which&nbsp<select class='filterValue'><option value='true'>exists</option><option value='false'>doesn't exist</option></select><label>"
			if (!['true','false'].includes(filters[i]['value']))
			{
				filters[i]['value'] = 'true'
				filters[i]['opt'] = false
			}
		}
		else
		{
			li.innerHTML += "containing&nbsp</label><input class='filterValue'>"
			filters[i]['opt'] = false
		}
		
		if(filters[i]['key'] == 'date')
		{
			li.querySelector('input').setAttribute('type','date')
		}
		
		li.querySelector('select').value = filters[i]['key']
		li.querySelector('.filterValue').value = filters[i]['value']
		
		
		li.querySelector('select').addEventListener('change',displayFilters)
		filterList.appendChild(li)
	}
}

//================================================

function filter(ll)
{
	//----------------------------------------------
	// Loads the list, leaves only filtered songs
	// and returns the levellist
	//----------------------------------------------
	
	let i = -1
	let filtered = []
	for (l of ll)
	{
		i += 1
		loop:
		for (f of filters)
		{
			switch (f['key'])
			{
				case 'title':
					if (!(l['title'][0].toLowerCase().includes(f['value'].toLowerCase()) || l['title'][1].toLowerCase().includes(f['value'].toLowerCase())))
					{
						filtered.push(i)
						break loop
					}
					break
				case 'author':
					if (!(l['author'][0].toLowerCase().includes(f['value'].toLowerCase()) || l['author'][1].toLowerCase().includes(f['value'].toLowerCase())))
					{
						filtered.push(i)
						break loop
					}
					break
				case 'authorId':
					if (!l['more']['authorId'].toLowerCase().includes(f['value'].toLowerCase()))
					{
						filtered.push(i)
						break loop
					}
					break
				case 'date':
					let date = new Date(f['value'] + ' 00:00').getTime() / 1000
					if (f['opt'] == 'before')
					{
						if (!(l['date'] < date))
						{
							filtered.push(i)
							break loop
						}
					}
					else
					{
						if (!(l['date'] > date))
						{
							filtered.push(i)
							break loop
						}
					}
					break
				case 'csinput':
					if (!(String(l['csinput']) == f['value']))
					{
						filtered.push(i)
						break loop
					}
					break
				case 'duration':
					if (f['opt'] == 'above')
					{
						if (!(l['duration'] > f['value']))
						{
							filtered.push(i)
							break loop
						}
					}
					else
					{
						if (!(l['duration'] < f['value']))
						{
							filtered.push(i)
							break loop
						}
					}
					break
				default:
					console.log('error - uknown filter key')
					break
			}
		}
	}
	filtered.reverse()
	for (i of filtered)
	{
		ll.splice(i,1)
	}
	return ll
}

//================================================

function setSorting(sortBy)
{
    /*let keys = ['no',"title", "author", "date", "downloads", "csinput", "rating", "duration", "i"]
    let th
    keys.forEach(function(key,no)
    {
        document.querySelector('th:nth-of-type(' + (no + 1) + ')').setAttribute('class','sorting')
        if (key == sortBy)
        {
            th = document.querySelector('th:nth-of-type(' + (no + 1) + ')')
        }
    })*/
    if (sortBy == sorting.sortBy)
    {
        sorting.sortDesc = !sorting.sortDesc
    }
    else
    {
        sorting.sortBy = sortBy
        sorting.sortDesc = true
    }
    /*
    if (sorting.sortDesc)
    {
        th.classList.add('desc')
    }
    else
    {
        th.classList.add('asc')
    }
    console.log(th.classList.value)*/
    applyDisplayOptions()
}