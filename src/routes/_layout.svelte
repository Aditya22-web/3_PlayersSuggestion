<script>
	// The 'segment' export has been removed as it was unused
</script>

<style>
	main {
		position: relative;
		max-width: 100%;
		background-color: white;
		padding: 1em;
		margin: 0 auto;
		box-sizing: border-box;
	}

	@media (min-width: 768px) {
		main {
			max-width: 56em;
			padding: 2em;
		}
	}
</style>

<main>
	<slot></slot>
</main>
