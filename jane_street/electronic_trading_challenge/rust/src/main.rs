use clap::Parser;
use jane_street_etc::exchange::ExchangeConnection;
use jane_street_etc::bot::TradingBot;
use anyhow::Result;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(long, default_value = "production")]
    host: String,

    #[arg(long, default_value_t = 25000)]
    port: u16,

    #[arg(long, default_value = "FOMO")]
    team: String,

    #[arg(short, long)]
    verbose: bool,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();

    if args.verbose {
        std::env::set_var("RUST_LOG", "debug");
    } else {
        std::env::set_var("RUST_LOG", "info");
    }
    env_logger::init();

    let conn = ExchangeConnection::connect(&args.host, args.port).await?;
    let mut bot = TradingBot::new(conn, args.team);
    
    bot.run().await?;
    
    Ok(())
}
