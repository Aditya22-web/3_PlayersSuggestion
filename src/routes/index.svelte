<script>
	import { onMount } from 'svelte';
	import { debounce } from 'lodash-es';

	let players = [];
	let selectedPlayers = Array(22).fill('');
	let pitchReport = '';
	let error = '';
	let isLoading = true;
	let filteredPlayers = Array(22).fill([]);
	let inputValues = Array(22).fill('');
	let showDropdown = Array(22).fill(false);

	onMount(async () => {
		try {
			const response = await fetch('/static/players.csv');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const data = await response.text();
			players = data.split('\n')
				.map(player => player.trim())
				.filter(player => player);
			isLoading = false;
		} catch (e) {
			console.error('Error fetching players:', e);
			error = 'Failed to load player data. Please try refreshing the page.';
			isLoading = false;
		}
	});

	const debouncedHandleInput = debounce((index, value) => {
		inputValues[index] = value;
		filteredPlayers[index] = players.filter(player =>
			player.toLowerCase().includes(value.toLowerCase())
		).slice(0, 10); // Limit to 10 suggestions
		showDropdown[index] = filteredPlayers[index].length > 0;
		selectedPlayers[index] = '';
		inputValues = inputValues;
		filteredPlayers = filteredPlayers;
		showDropdown = showDropdown;
	}, 300);

	function handleInput(index, value) {
		debouncedHandleInput(index, value);
	}

	function selectPlayer(index, player) {
		selectedPlayers[index] = player;
		inputValues[index] = player;
		showDropdown[index] = false;
		selectedPlayers = selectedPlayers;
		inputValues = inputValues;
		showDropdown = showDropdown;
	}

	function handleSubmit() {
		error = '';

		if (selectedPlayers.some(player => !player)) {
			error = 'Please select all 22 players before submitting.';
			return;
		}
		if (!pitchReport.trim()) {
			error = 'Please provide a pitch report before submitting.';
			return;
		}

		console.log('Selected players:', selectedPlayers);
		console.log('Pitch report:', pitchReport);
		console.log('Form submitted successfully!');
	}
</script>

<style>
	.container {
		max-width: 800px;
		margin: 0 auto;
		padding: 20px;
	}

	h1 {
		text-align: center;
		color: #333;
	}

	.player-inputs {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 10px;
		margin-bottom: 20px;
	}

	.pitch-report {
		margin-bottom: 20px;
	}

	textarea {
		width: 100%;
		height: 100px;
		resize: vertical;
	}

	button {
		display: block;
		width: 100%;
		padding: 10px;
		background-color: #4CAF50;
		color: white;
		border: none;
		cursor: pointer;
		font-size: 16px;
	}

	button:hover {
		background-color: #45a049;
	}

	.error {
		color: red;
		text-align: center;
		margin-bottom: 10px;
	}

	.autocomplete {
		position: relative;
	}

	.autocomplete input {
		width: 100%;
		padding: 8px;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	.autocomplete-items {
		position: absolute;
		border: 1px solid #d4d4d4;
		border-top: none;
		z-index: 99;
		top: 100%;
		left: 0;
		right: 0;
		max-height: 200px;
		overflow-y: auto;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.autocomplete-items li {
		padding: 10px;
		cursor: pointer;
		background-color: #fff;
		border-bottom: 1px solid #d4d4d4;
	}

	.autocomplete-items li:hover {
		background-color: #e9e9e9;
	}

	@media (max-width: 600px) {
		.player-inputs {
			grid-template-columns: 1fr;
		}
	}
</style>

<svelte:head>
	<title>Fantasy Cricket App</title>
</svelte:head>

<div class="container">
	<h1>Fantasy Cricket Team Selection</h1>

	{#if error}
		<p class="error">{error}</p>
	{:else if isLoading}
		<p>Loading player data...</p>
	{:else}
		<div class="player-inputs">
			{#each Array(22) as _, i (i)}
				<div class="autocomplete">
					<input
						type="text"
						placeholder={`Player ${i + 1}`}
						bind:value={inputValues[i]}
						on:input={() => handleInput(i, inputValues[i])}
					/>
					{#if showDropdown[i] && filteredPlayers[i].length > 0}
						<ul class="autocomplete-items">
							{#each filteredPlayers[i] as player}
								<li on:click={() => selectPlayer(i, player)}>{player}</li>
							{/each}
						</ul>
					{/if}
				</div>
			{/each}
		</div>

		<div class="pitch-report">
			<h2>Pitch Report</h2>
			<textarea bind:value={pitchReport} placeholder="Enter detailed pitch conditions..."></textarea>
		</div>

		<button on:click={handleSubmit}>Submit Team</button>
	{/if}
</div>
