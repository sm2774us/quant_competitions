use clap::Parser;
use citadel_bot::api::RealTradingApi;
use citadel_bot::bot::TradingBot;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(long, default_value = "http://localhost:9998")]
    url: String,

    #[arg(long)]
    key: String,

    #[arg(long, default_value_t = 0.1)]
    interval: f64,
}

fn main() {
    let args = Args::parse();
    
    let api = RealTradingApi::new(args.url, args.key);
    let mut bot = TradingBot::new(&api);
    
    bot.start(args.interval);
}
