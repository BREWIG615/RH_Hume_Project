"""
Delta Lake Processing Engine

Abstraction layer for data processing with Delta Lake.
Supports both local (delta-rs) and Databricks environments.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class DataEngine(ABC):
    """Abstract interface for data processing engines."""
    
    @abstractmethod
    def read_delta(self, path: str) -> pd.DataFrame:
        """Read Delta table."""
        pass
    
    @abstractmethod
    def write_delta(
        self,
        df: pd.DataFrame,
        path: str,
        mode: str = "overwrite",
        partition_by: Optional[list[str]] = None
    ):
        """Write DataFrame to Delta table."""
        pass
    
    @abstractmethod
    def read_parquet(self, path: str) -> pd.DataFrame:
        """Read Parquet file(s)."""
        pass
    
    @abstractmethod
    def write_parquet(self, df: pd.DataFrame, path: str):
        """Write DataFrame to Parquet."""
        pass
    
    @abstractmethod
    def table_exists(self, path: str) -> bool:
        """Check if Delta table exists."""
        pass


class LocalDeltaEngine(DataEngine):
    """
    Local Delta Lake engine using delta-rs.
    
    For development and testing without Databricks.
    
    Example:
        engine = LocalDeltaEngine(base_path="data")
        df = engine.read_delta("processed/facilities")
        engine.write_delta(df, "presentation/facilities", mode="overwrite")
    """
    
    def __init__(self, base_path: str = "data"):
        """
        Initialize local Delta engine.
        
        Args:
            base_path: Base directory for data files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Import here to fail fast if not installed
        try:
            import deltalake
            self._deltalake = deltalake
            logger.info(f"LocalDeltaEngine initialized: {base_path}")
        except ImportError:
            logger.warning("deltalake not installed, Delta operations will fail")
            self._deltalake = None
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve relative path to absolute."""
        if Path(path).is_absolute():
            return Path(path)
        return self.base_path / path
    
    def read_delta(self, path: str) -> pd.DataFrame:
        """Read Delta table to pandas DataFrame."""
        full_path = self._resolve_path(path)
        
        if self._deltalake is None:
            raise RuntimeError("deltalake not installed")
        
        try:
            dt = self._deltalake.DeltaTable(str(full_path))
            return dt.to_pandas()
        except Exception as e:
            logger.error(f"Failed to read Delta table {path}: {e}")
            raise
    
    def write_delta(
        self,
        df: pd.DataFrame,
        path: str,
        mode: str = "overwrite",
        partition_by: Optional[list[str]] = None
    ):
        """
        Write DataFrame to Delta table.
        
        Args:
            df: DataFrame to write
            path: Table path
            mode: Write mode (overwrite, append)
            partition_by: Columns to partition by
        """
        full_path = self._resolve_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self._deltalake is None:
            raise RuntimeError("deltalake not installed")
        
        try:
            # Convert to PyArrow table
            import pyarrow as pa
            table = pa.Table.from_pandas(df)
            
            self._deltalake.write_deltalake(
                str(full_path),
                table,
                mode=mode,
                partition_by=partition_by,
                overwrite_schema=True
            )
            
            logger.info(f"Wrote {len(df)} rows to Delta table: {path}")
            
        except Exception as e:
            logger.error(f"Failed to write Delta table {path}: {e}")
            raise
    
    def read_parquet(self, path: str) -> pd.DataFrame:
        """Read Parquet file(s) to pandas DataFrame."""
        full_path = self._resolve_path(path)
        
        try:
            return pd.read_parquet(full_path)
        except Exception as e:
            logger.error(f"Failed to read Parquet {path}: {e}")
            raise
    
    def write_parquet(self, df: pd.DataFrame, path: str):
        """Write DataFrame to Parquet."""
        full_path = self._resolve_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            df.to_parquet(full_path, index=False)
            logger.info(f"Wrote {len(df)} rows to Parquet: {path}")
        except Exception as e:
            logger.error(f"Failed to write Parquet {path}: {e}")
            raise
    
    def table_exists(self, path: str) -> bool:
        """Check if Delta table exists."""
        full_path = self._resolve_path(path)
        return (full_path / "_delta_log").exists()
    
    def read_csv(self, path: str, **kwargs) -> pd.DataFrame:
        """Read CSV file."""
        full_path = self._resolve_path(path)
        return pd.read_csv(full_path, **kwargs)
    
    def write_csv(self, df: pd.DataFrame, path: str, **kwargs):
        """Write DataFrame to CSV."""
        full_path = self._resolve_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(full_path, index=False, **kwargs)
        logger.info(f"Wrote {len(df)} rows to CSV: {path}")
    
    def list_tables(self, prefix: str = "") -> list[str]:
        """List Delta tables with optional prefix."""
        search_path = self._resolve_path(prefix) if prefix else self.base_path
        
        tables = []
        if search_path.exists():
            for path in search_path.rglob("_delta_log"):
                table_path = path.parent.relative_to(self.base_path)
                tables.append(str(table_path))
        
        return tables


class DatabricksEngine(DataEngine):
    """
    Databricks Delta Lake engine.
    
    For production environments with full Spark capabilities.
    
    Note: Requires running in Databricks environment.
    """
    
    def __init__(self, catalog: str = "hive_metastore", schema: str = "default"):
        """
        Initialize Databricks engine.
        
        Args:
            catalog: Unity Catalog catalog name
            schema: Database schema name
        """
        self.catalog = catalog
        self.schema = schema
        
        try:
            from pyspark.sql import SparkSession
            self.spark = SparkSession.builder.getOrCreate()
            logger.info(f"DatabricksEngine initialized: {catalog}.{schema}")
        except Exception as e:
            logger.error(f"Failed to initialize Spark: {e}")
            raise
    
    def _full_table_name(self, table: str) -> str:
        """Get fully qualified table name."""
        if "." in table:
            return table
        return f"{self.catalog}.{self.schema}.{table}"
    
    def read_delta(self, path: str) -> pd.DataFrame:
        """Read Delta table."""
        if path.startswith("/") or path.startswith("dbfs:"):
            # Path-based access
            spark_df = self.spark.read.format("delta").load(path)
        else:
            # Table name access
            spark_df = self.spark.table(self._full_table_name(path))
        
        return spark_df.toPandas()
    
    def write_delta(
        self,
        df: pd.DataFrame,
        path: str,
        mode: str = "overwrite",
        partition_by: Optional[list[str]] = None
    ):
        """Write DataFrame to Delta table."""
        spark_df = self.spark.createDataFrame(df)
        
        writer = spark_df.write.format("delta").mode(mode)
        
        if partition_by:
            writer = writer.partitionBy(*partition_by)
        
        if path.startswith("/") or path.startswith("dbfs:"):
            writer.save(path)
        else:
            writer.saveAsTable(self._full_table_name(path))
        
        logger.info(f"Wrote {len(df)} rows to Delta: {path}")
    
    def read_parquet(self, path: str) -> pd.DataFrame:
        """Read Parquet file(s)."""
        return self.spark.read.parquet(path).toPandas()
    
    def write_parquet(self, df: pd.DataFrame, path: str):
        """Write DataFrame to Parquet."""
        spark_df = self.spark.createDataFrame(df)
        spark_df.write.parquet(path, mode="overwrite")
    
    def table_exists(self, path: str) -> bool:
        """Check if Delta table exists."""
        try:
            self.spark.table(self._full_table_name(path))
            return True
        except Exception:
            return False
    
    def run_sql(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return results."""
        return self.spark.sql(query).toPandas()


def get_data_engine(
    engine_type: str = "local",
    **kwargs
) -> DataEngine:
    """
    Factory function to get data engine.
    
    Args:
        engine_type: Engine type ("local" or "databricks")
        **kwargs: Additional engine arguments
        
    Returns:
        DataEngine instance
    """
    if engine_type == "local":
        return LocalDeltaEngine(**kwargs)
    elif engine_type == "databricks":
        return DatabricksEngine(**kwargs)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")
