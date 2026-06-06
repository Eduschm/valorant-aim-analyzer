import { Star } from 'lucide-react'

/** Fabricated reviews — placeholder social proof until real testimonials exist. */
const REVIEWS = [
  {
    name: 'Marcus "vyn" L.',
    rank: 'Diamond 2',
    initial: 'M',
    quote:
      'It told me my first-bullet HS% dropped to 18% on eco rounds. Fixed my buy discipline and climbed out of Plat in two weeks.',
  },
  {
    name: 'Sofia R.',
    rank: 'Ascendant 1',
    initial: 'S',
    quote:
      'Every other coach gave me generic "crosshair placement" advice. This pointed at my exact ADR drop on defense and why.',
  },
  {
    name: 'Kenji T.',
    rank: 'Immortal 3',
    initial: 'K',
    quote:
      'The report reads like a teammate who actually looked at my match history. Specific numbers, no fluff. Worth it.',
  },
  {
    name: 'Dani P.',
    rank: 'Gold 3',
    initial: 'D',
    quote:
      'Found out I was overshooting on 40% of my whiffs. Ran the drills it suggested and my win rate went from 47% to 58%.',
  },
  {
    name: 'Aaron "blip" K.',
    rank: 'Platinum 1',
    initial: 'A',
    quote:
      'I check it after every session now. Watching my HS% trend climb week over week is genuinely motivating.',
  },
  {
    name: 'Lena M.',
    rank: 'Ascendant 3',
    initial: 'L',
    quote:
      'Cancelled my $25/mo coaching sub. This costs a fraction and the feedback is sharper because it is tied to my real stats.',
  },
]

export function Testimonials() {
  return (
    <section className="relative mx-auto max-w-6xl px-6 py-20">
      <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">What players say</p>
      <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
        Trusted by climbers at every rank
      </h2>

      <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {REVIEWS.map((r) => (
          <figure key={r.name} className="glass flex h-full flex-col rounded-xl p-6">
            <div className="mb-3 flex gap-0.5 text-val-accent">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star key={i} className="h-3.5 w-3.5 fill-current" />
              ))}
            </div>
            <blockquote className="flex-1 text-sm leading-relaxed text-[#C7CDDA]">
              &ldquo;{r.quote}&rdquo;
            </blockquote>
            <figcaption className="mt-5 flex items-center gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-val-accent/15 font-display text-sm font-bold text-val-accent">
                {r.initial}
              </span>
              <span className="text-sm">
                <span className="block font-semibold text-[#F0F1F5]">{r.name}</span>
                <span className="block text-xs text-[#7A8496]">{r.rank}</span>
              </span>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  )
}
