/*
! not used anymore
function removeFromDict(dict,keys)
{
	for (key of keys)
	{
		delete dict[key]
	}
	return dict
}*/

//================================================

function sortByKey(array, key) 
{
    return array.sort(function(a, b) 
    {
        var x = a[key]
        var y = b[key]
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
    let l = ll[no]
    
	let data = ''
	data += '<div><div>Title: <a href="https://projectdxxx.me/score/index/id/' + l.id + '">' + l.jpTitle + '</a>'
	if (l.title != l.jpTitle)
	{
		data += '<br>Title (converted): ' + l.title
	}
	data += '<br>Author: ' + l.jpAuthor
	if (l.author != l.jpAuthor)
	{
		data += '<br>Author (converted): ' + l.author
	}
	data += '<br>Author ID: <a href="https://projectdxxx.me/user/index/id/' + l.authorId + '"><img src="https://projectdxxx.me/api/get-avator/s/16/id/' + l.authorId + '"> ' + l.authorId + '</a>'
	data += '<br>Upload date: ' + new Date(l.date*1000).toLocaleDateString()
	data += '<br>CSInput: '
	if (l.csinput) {data += '✔️'}
	else {data += '❌'}
	data += '<br>Downloads: ' + l.downloads
	data += '<br>Rating: '
	if (l.voted == 0) {data += '-'}
	else
	{
		data += l.rating.toFixed(2)
	}
	data += '<br>Votes: '
	if (l.voted == 0) {data += '-'}
	else
	{
		data += l.voted
	}
	//data += '<br>Duration: ' + new Date(ll[no]['duration']*1000).toISOString().substring(14, 19)
    data += '<br>Duration: ' + convertDuration(l.duration)
	data += '<br>BPM: ' + l.bpm
	
	
	
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
	let desc = l.desc.replace('\n','').replaceAll('\n','<br>').replaceAll('[Lock]','')
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
		if (l['p' + diff] != 0)
		{
			data += '<br>' + diff + ' - '
            //if stars exist
			if (l['s' + diff] != '')
			{
                if (!l['a' + diff])
                {
				    data += '<span>☆' + l['s' + diff] + '</span> (' + l['p' + diff] + ' pt)'
                }
                //if stars are approximated
                else
                {
                    data += '<span class="approx">☆' + l['s' + diff] + '</span> (' + l['p' + diff] + ' pt)'
                }
			}
			else
			{
				data += l['p' + diff] + ' pt'
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
		l.levellistId = levellistId
		
		l.downloads = Number(l.downloads)
		l.rating = Number(l.rating)
        l.bpm = Number(l.bpm)
        l.voted = Number(l.voted)
        
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
		
        l.pEasy = Number(l.pEasy)
        l.pNormal = Number(l.pNormal)
        l.pHard = Number(l.pHard)
        l.pExtreme = Number(l.pExtreme)
		
		let duration = l.duration
		duration = duration.split(':')
		duration = Number(duration[0] * 60) + Number(duration[1])
		l.duration = duration
		
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
	
	//romaji = !romaji
	//ll = ll.slice(0,maxrows)
	
	let no = 1
	for (l of ll)
	{
        if (!romaji)
        {
            l.title = l.jpTitle
            l.author = l.jpAuthor
        }
		
		l.date = new Date(l.date*1000).toLocaleDateString()
		l.duration = convertDuration(l.duration)
		
		if (l.csinput) {l.csinput = '✔️'}
		else {l.csinput = '❌'}
		
		if (l.voted == 0) {l.rating = '-'}
		
		if (!isNaN(l.rating)) 
		{
			//l['rating'] = Number(l['rating']).toFixed(2)
			l.rating += ' (' + l.voted + ')'
		}
		
		l.no = no
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
    
    let skeys = ['no','title', 'author', 'date', 'csinput', 'downloads', 'rating', 'duration', 'sExtreme', 'i']
	
    let table = document.createElement('table')
    let tbody = document.createElement('tbody')
    let row = document.createElement('tr')
    for (let n = 0; n < dkeys.length; n += 1)
    {
        let cell = document.createElement('th')
        let dkey = dkeys[n]
        let skey = skeys[n]
        /*
        if (['No.','More'].includes(key))
        {
            cell.innerText = key
        }
        else
        {
            cell.innerHTML = '<span class="sorting">' + key + '</span>'
        }*/
        
        if (!['no','i'].includes(skey))
        {
            cell.classList.add('sorting')
            cell.setAttribute('onclick','setSorting("' + skey + '")')
        }
        cell.innerText = dkey
        
        if (skey == 'sExtreme')
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
    for (let l of ll)
    {
        let row = document.createElement('tr')
        for (let key of keys)
        {
            let cell = document.createElement('td')
            
            if (key == 'title')
            {
                let a = document.createElement('a')
                a.setAttribute('href','https://projectdxxx.me/score/index/id/' + l.id)
                a.innerText = l[key]
                cell.appendChild(a)
            }
            else if (key == 'author')
            {
                let a = document.createElement('a')
                //a.setAttribute('href','#')
                a.setAttribute('href','https://projectdxxx.me/user/index/id/' + l.authorId)
                a.innerText = l[key]
                cell.appendChild(a)
            }
            else if (['sEasy', 'sNormal', 'sHard', 'sExtreme'].includes(key))
            {
                if (['sEasy', 'sNormal'].includes(key)&&lessDiff)
                {
                    continue
                }
                
                
                //if stars exist
                if (l[key] != '')
                {
                    let diff = key.slice(1)
                    if (!l['a' + diff])
                    {
                        cell.innerHTML = '<span>☆' + l['s' + diff] + '</span>'
                    }
                    //if stars are approximated
                    else
                    {
                        cell.innerHTML = '<span class="approx">☆' + l['s' + diff] + '</span>'
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
				cell.setAttribute('levellistId',l.levellistId)
			}
            else
            {
                cell.innerText = l[key]
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
    skeys.forEach(function(skey,no)
    {
        //document.querySelector('th:nth-of-type(' + (no + 1) + ')').setAttribute('class','sorting')
        if (skey == sorting.sortBy)
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
        let f = filters[i]
        let nf = newFilters[i]
		if (['date','duration'].includes(f.key))
		{
			f.opt = nf.querySelector('select:nth-of-type(2)').value
			f.value = nf.querySelector('input').value
		}
		else if (f.key == 'csinput')
		{
			f.value = nf.querySelector('select:nth-of-type(2)').value
		}
		else
		{
			f.opt = false
			f.value = nf.querySelector('input').value
		}
		
		f.key = nf.querySelector('select').value
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
        let f = filters[i]
        
		let li = document.createElement('li')
		li.innerHTML = "<label>Filter by&nbsp</label><select><option value='title'>title</option><option value='author'>author</option><option value='authorId'>author ID</option><option value='date'>upload date</option><option value='csinput'>CSInput</option><option value='duration'>duration</option></select>&nbsp"
		if (f.key == 'date')
		{
			li.innerHTML += "<select><option value='before'>before</option><option value='after'>after</option></select><label>&nbsp</label><input type='date' class='filterValue'>"
			if (!['before','after'].includes(f.opt))
			{
				f.opt = 'before'
			}
			li.querySelector('select:nth-of-type(2)').value = f.opt
			
		}
		else if (f.key == 'duration')
		{
			li.innerHTML += "<select><option value='above'>above</option><option value='below'>below</option></select><label>&nbsp</label><input type='number' min=0 max=9999 class='filterValue'>"
			if (!['above','below'].includes(f.opt))
			{
				f.opt = 'above'
			}
			li.querySelector('select:nth-of-type(2)').value = f.opt
		}
		else if (f.key == 'csinput')
		{
			li.innerHTML += "which&nbsp<select class='filterValue'><option value='true'>exists</option><option value='false'>doesn't exist</option></select><label>"
			if (!['true','false'].includes(f.value))
			{
				f.value = 'true'
				f.opt = false
			}
		}
		else
		{
			li.innerHTML += "containing&nbsp</label><input class='filterValue'>"
			f.opt = false
		}
		
		if(f.key == 'date')
		{
			li.querySelector('input').setAttribute('type','date')
		}
		
		li.querySelector('select').value = f.key
		li.querySelector('.filterValue').value = f.value
		
		
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
			switch (f.key)
			{
				case 'title':
					if (!(l.title.toLowerCase().includes(f.value.toLowerCase()) || l.jpTitle.toLowerCase().includes(f.value.toLowerCase())))
					{
						filtered.push(i)
						break loop
					}
					break
				case 'author':
					if (!(l.author.toLowerCase().includes(f.value.toLowerCase()) || l.jpAuthor.toLowerCase().includes(f.value.toLowerCase())))
					{
						filtered.push(i)
						break loop
					}
					break
				case 'authorId':
					if (!l.authorId.toLowerCase().includes(f.value.toLowerCase()))
					{
						filtered.push(i)
						break loop
					}
					break
				case 'date':
					let date = new Date(f.value + ' 00:00').getTime() / 1000
					if (f.opt == 'before')
					{
						if (!(l.date < date))
						{
							filtered.push(i)
							break loop
						}
					}
					else
					{
						if (!(l.date > date))
						{
							filtered.push(i)
							break loop
						}
					}
					break
				case 'csinput':
					if (!(String(l.csinput) == f.value))
					{
						filtered.push(i)
						break loop
					}
					break
				case 'duration':
					if (f.opt == 'above')
					{
						if (!(l.duration > f.value))
						{
							filtered.push(i)
							break loop
						}
					}
					else
					{
						if (!(l.duration < f.value))
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