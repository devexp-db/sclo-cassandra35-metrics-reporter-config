Name:           metrics-reporter-config
Version:        3.0.0
Release:        1%{?dist}
Summary:        Manages config for metrics from Coda Hale’s Metrics library

License:        ASL 2.0
URL:            https://github.com/addthis/%{name}
Source0:        https://github.com/addthis/%{name}/archive/v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  maven-local
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.hibernate:hibernate-validator)
BuildRequires:  mvn(org.slf4j:slf4j-api)
BuildRequires:  mvn(org.slf4j:slf4j-simple)
BuildRequires:  mvn(com.codahale.metrics:metrics-ganglia)
BuildRequires:  mvn(com.codahale.metrics:metrics-core)
BuildRequires:  mvn(com.codahale.metrics:metrics-graphite)
BuildRequires:  mvn(org.yaml:snakeyaml)
BuildRequires:  mvn(org.mockito:mockito-all)

# https://bugzilla.redhat.com/show_bug.cgi?id=1306629#c2
BuildRequires:  mvn(org.apache.commons:commons-lang3)

%description
Coda Hale's Metrics package makes it easy to create useful metrics so you
know what is going on in production. In addition to showing up in the
normal Java places (JMX), Metrics supports an arbitrary number of Reporters
(where to send the application telemetry to make pretty graphs).
Ganglia and Graphite (or both) are among the most popular choices.

However, Metrics purposefully doesn't come with a kitchen sink of support for
every dependency injection or configuration tool yet devised by Java
developers. Metrics-Reporter-Config aims to provide a simple way to configure
and enable a set of Reporters that can be shared among applications. It
should fit most (say 90% of) use cases and avoid situations like a plethora
of subtly incompatible properties files.

%package        javadoc
Summary:        Javadoc for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q

%mvn_alias :reporter-config3 :reporter-config
%mvn_file :reporter-config3 %{name}/reporter-config

%pom_remove_parent
%pom_disable_module reporter-config2
%pom_xpath_set "pom:version[text()='\${dep.slf4j.version}']" "1.7.14"
%pom_xpath_set "pom:version[text()='\${dep.guava.version}']" "19.0"
# missing org.junit
%pom_add_dep junit:junit::test
# remove for fedora 24
%pom_change_dep io.dropwizard.metrics: com.codahale.metrics: reporter-config3/pom.xml

%build
%mvn_build -- -Dproject.build.sourceEncoding=UTF-8

%install
%mvn_install

%files -f .mfiles
%doc README.mdown
%license LICENSE NOTICE

%files javadoc -f .mfiles-javadoc
%license LICENSE NOTICE

%changelog
* Wed Mar 23 2016 Tomas Repik <trepik@redhat.com> - 3.0.0-1
- Initial RPM release

