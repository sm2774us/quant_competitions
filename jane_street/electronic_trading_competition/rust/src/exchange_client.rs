use tokio::net::TcpStream;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use anyhow::{Result, anyhow};
use crate::models::{ExchangeMessage, Order};
use serde_json;

pub struct ExchangeClient {
    writer: tokio::net::tcp::OwnedWriteHalf,
    reader: BufReader<tokio::net::tcp::OwnedReadHalf>,
}

impl ExchangeClient {
    pub async fn connect(hostname: &str, port: u16, team: &str) -> Result<Self> {
        let stream = TcpStream::connect(format!("{}:{}", hostname, port)).await?;
        let (reader, mut writer) = stream.into_split();
        
        let hello = serde_json::json!({
            "type": "hello",
            "team": team.to_uppercase()
        });
        writer.write_all(format!("{}
", hello).as_bytes()).await?;

        Ok(Self {
            writer,
            reader: BufReader::new(reader),
        })
    }

    pub async fn send_order(&mut self, order: &Order) -> Result<()> {
        let data = serde_json::to_string(order)?;
        self.writer.write_all(format!("{}
", data).as_bytes()).await?;
        Ok(())
    }

    pub async fn next_message(&mut self) -> Result<Option<ExchangeMessage>> {
        let mut line = String::new();
        let n = self.reader.read_line(&mut line).await?;
        if n == 0 { return Ok(None); }
        let msg: ExchangeMessage = serde_json::from_str(&line)?;
        Ok(Some(msg))
    }
}
