"""
Job Runner CLI

Command-line interface for running batch jobs.

Usage:
    python -m jobs.runner generate_data
    python -m jobs.runner etl
    python -m jobs.runner full_pipeline
"""

import click
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@click.group()
@click.option("--config", default="config", help="Config directory")
@click.pass_context
def cli(ctx, config):
    """RH Hume Project Job Runner"""
    ctx.ensure_object(dict)
    ctx.obj["config_dir"] = config


@cli.command()
@click.option("--count", default=None, type=int, help="Override record counts")
@click.option("--scenario", default="baseline", help="Scenario: baseline, disrupted")
@click.pass_context
def generate_data(ctx, count, scenario):
    """Generate synthetic demo data."""
    logger.info(f"Generating synthetic data: scenario={scenario}")
    from jobs.synthetic_data import generate_all
    generate_all(scenario=scenario, count_override=count)
    logger.info("Data generation complete")


@cli.command()
@click.pass_context
def etl(ctx):
    """Run ETL pipeline."""
    logger.info("Running ETL pipeline")
    from jobs.etl_pipeline import run_etl
    run_etl()
    logger.info("ETL complete")


@cli.command()
@click.pass_context  
def load_neo4j(ctx):
    """Load data into Neo4j."""
    logger.info("Loading data into Neo4j")
    from jobs.neo4j_loader_job import load_all
    load_all()
    logger.info("Neo4j load complete")


@cli.command()
@click.pass_context
def hume_batch(ctx):
    """Process communications through Hume."""
    logger.info("Running Hume batch processing")
    from jobs.hume_processor import process_batch
    process_batch()
    logger.info("Hume processing complete")


@cli.command()
@click.pass_context
def embeddings(ctx):
    """Generate embeddings for RAG."""
    logger.info("Generating embeddings")
    from jobs.embedding_generator import generate_embeddings
    generate_embeddings()
    logger.info("Embeddings complete")


@cli.command()
@click.pass_context
def aggregations(ctx):
    """Run aggregation calculations."""
    logger.info("Running aggregations")
    from jobs.aggregation import run_aggregations
    run_aggregations()
    logger.info("Aggregations complete")


@cli.command()
@click.pass_context
def qlik_presentation(ctx):
    """Generate Qlik presentation layer."""
    logger.info("Generating Qlik presentation layer")
    from jobs.qlik_presentation import generate_presentation_layer
    generate_presentation_layer()
    logger.info("Qlik presentation complete")


@cli.command()
@click.pass_context
def narratives(ctx):
    """Generate AI narratives for dashboards."""
    logger.info("Generating narratives")
    from jobs.narrative_generator import generate_narratives
    generate_narratives()
    logger.info("Narratives complete")


@cli.command()
@click.pass_context
def full_pipeline(ctx):
    """Run full processing pipeline."""
    logger.info("=" * 60)
    logger.info("Starting full pipeline")
    logger.info("=" * 60)
    
    start = datetime.now()
    
    ctx.invoke(generate_data)
    ctx.invoke(etl)
    ctx.invoke(load_neo4j)
    ctx.invoke(hume_batch)
    ctx.invoke(embeddings)
    ctx.invoke(aggregations)
    ctx.invoke(qlik_presentation)
    ctx.invoke(narratives)
    
    elapsed = datetime.now() - start
    logger.info("=" * 60)
    logger.info(f"Full pipeline complete in {elapsed}")
    logger.info("=" * 60)


@cli.command()
@click.option("--snapshot", required=True, help="Snapshot name: baseline, disrupted, recovery")
@click.pass_context
def load_snapshot(ctx, snapshot):
    """Load a data snapshot."""
    logger.info(f"Loading snapshot: {snapshot}")
    from jobs.snapshot_loader import load_snapshot as _load
    _load(snapshot)
    logger.info("Snapshot loaded")


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
