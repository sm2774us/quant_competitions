mod models;
mod exchange;
mod strategy;
mod bot;

use clap::Parser;
use crate::bot::Bot;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(long, default_value = "localhost")]
    host: String,

    #[arg(long, default_value_t = 25000)]
    port: u16,

    #[arg(long, default_value = "TEAMNAME")]
    team: String,
}

fn main() -> anyhow::Result<()> {
    env_logger::init();
    let args = Args::parse();

    let mut bot = Bot::new(&args.host, args.port, &args.team)?;
    bot.run()?;

    Ok(())
}
