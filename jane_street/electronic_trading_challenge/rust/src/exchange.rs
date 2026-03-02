use anyhow::Result;
use serde_json::{json, Value};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::TcpStream;

pub struct ExchangeConnection {
    reader: BufReader<tokio::net::tcp::OwnedReadHalf>,
    writer: tokio::net::tcp::OwnedWriteHalf,
}

impl ExchangeConnection {
    pub async fn connect(host: &str, port: u16) -> Result<Self> {
        let stream = TcpStream::connect(format!("{}:{}", host, port)).await?;
        let (read, write) = stream.into_split();
        Ok(Self {
            reader: BufReader::new(read),
            writer: write,
        })
    }

    pub async fn read(&mut self) -> Result<Option<Value>> {
        let mut line = String::new();
        let n = self.reader.read_line(&mut line).await?;
        if n == 0 {
            return Ok(None);
        }
        Ok(Some(serde_json::from_str(&line)?))
    }

    pub async fn write(&mut self, message: Value) -> Result<()> {
        let mut data = serde_json::to_string(&message)?;
        data.push('
');
        self.writer.write_all(data.as_bytes()).await?;
        Ok(())
    }

    pub async fn send_hello(&mut self, team: &str) -> Result<()> {
        self.write(json!({"type": "hello", "team": team})).await
    }

    pub async fn place_order(&mut self, id: i32, sym: &str, dir: &str, price: i32, size: i32) -> Result<()> {
        self.write(json!({
            "type": "add",
            "order_id": id,
            "symbol": sym,
            "dir": dir,
            "price": price,
            "size": size
        })).await
    }

    pub async fn convert(&mut self, id: i32, sym: &str, dir: &str, size: i32) -> Result<()> {
        self.write(json!({
            "type": "convert",
            "order_id": id,
            "symbol": sym,
            "dir": dir,
            "size": size
        })).await
    }
}
