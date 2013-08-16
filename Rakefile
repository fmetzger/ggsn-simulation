require "i18n"
require "active_support/all"
require "benchmark"
require "csv"

task :clean do
  #TODO
end


task :simulate, :number_of_parallel_tasks do |task, args|
  number_of_parallel_tasks = (args[:number_of_parallel_tasks] || 3).to_i
  numberOfRuns = 10
  duration = 25.hours
  numberOfResources = (1..101).step(10)

  metaSeed = 13
  maxSeed = 2**(32 - 1) - 1
  rng = Random.new(metaSeed)
  seeds = (1..numberOfRuns).map { rng.rand(maxSeed) }

  python_interpreter = if File.exists?('../../simpy-env/bin/pypy')
                         '../../simpy-env/bin/pypy'
                       else
                         'pypy'
                       end

  threads = []

  numberOfResources.in_groups(number_of_parallel_tasks, false) do |current_number_of_resources|
    threads << Thread.new do
      local_time = {}
      current_number_of_resources.each do |n|
        replication_times = []
        seeds.each_with_index do |seed, i|
          time = Benchmark.realtime do
            `#{python_interpreter} traditional_ggsn.py -d#{ duration.to_i } -n#{ n } -s#{ seed }`
          end
          time = time.round(2)
          puts "Number of resources: #{ n } (#{i} / #{numberOfRuns}) completed in #{ time } (s).\n"
          replication_times << time
        end
        local_time[n] = replication_times
      end
      Thread.current[:local_time] = local_time
    end
  end

  overall_times = {}

  threads.each do |thread|
    thread.join
    local_time = thread[:local_time]
    local_time.each do |number_of_resources, times|
      overall_times[number_of_resources] = times
    end
  end

  aggregated_overall_times = []
  numberOfResources.each do |current_number_of_resources|
    aggregated_overall_times << overall_times[current_number_of_resources]
  end

  CSV.open("results/time.csv", "wb", col_sep: ";", headers: ["seed"] + numberOfResources) do |csv|
    seeds.zip(aggregated_overall_times.transpose).each do |seed, times|
      csv << ([seed] + times)
    end
  end
end

task :default => [:simulate]
