<script>
  import Index from './routes/index.svelte';
</script>

<main>
  <Index />
</main>

<style>
  main {
    max-width: 100%;
    margin: 0 auto;
    padding: 1rem;
  }

  @media (min-width: 768px) {
    main {
      max-width: 56em;
      padding: 2rem;
    }
  }
</style>
