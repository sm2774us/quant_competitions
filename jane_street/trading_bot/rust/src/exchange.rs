use std::io::{BufRead, BufReader, Write};
use std::net::TcpStream;
use anyhow::{Result, Context};
use crate::models::{ClientMessage, ExchangeMessage};

pub struct Exchange {
    stream: TcpStream,
    reader: BufReader<TcpStream>,
}

impl Exchange {
    pub fn connect(host: &str, port: u16) -> Result<Self> {
        let stream = TcpStream::connect(format!("{}:{}", host, port))
            .with_context(|| format!("Failed to connect to {}:{}", host, port))?;
        let reader = BufReader::new(stream.try_clone()?);
        Ok(Self { stream, reader })
    }

    pub fn send(&mut self, message: &ClientMessage) -> Result<()> {
        let mut data = serde_json::to_string(message)?;
        data.push('
');
        self.stream.write_all(data.as_bytes())?;
        Ok(())
    }

    pub fn receive(&mut self) -> Result<Option<ExchangeMessage>> {
        let mut line = String::new();
        let bytes_read = self.reader.read_line(&mut line)?;
        if bytes_read == 0 {
            return Ok(None);
        }
        let message = serde_json::from_str(&line)?;
        Ok(Some(message))
    }
}
